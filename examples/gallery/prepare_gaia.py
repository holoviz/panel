"""Build the Gaia DR3 extract served by the Million-Star Atlas gallery app.

Source: ESA Gaia Archive, gaiadr3.gaia_source (https://gea.esac.esa.int/archive/).
License: CC BY-NC 3.0 IGO. Credit ESA/Gaia/DPAC when using this extract.
"""

from __future__ import annotations

import argparse
import logging

from io import StringIO
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import requests

TAP_URL = "https://gea.esac.esa.int/tap-server/tap/sync"
LOGGER = logging.getLogger(__name__)
STOP = 12_000_000
CHUNK = 1_000_000
COLUMNS = ("source_id", "l", "b", "bp_rp", "phot_g_mean_mag", "parallax", "parallax_over_error")
FILTER = "parallax_over_error > 5 AND bp_rp IS NOT NULL"


def download_chunk(session: requests.Session, start: int, stop: int) -> pd.DataFrame:
    query = (
        f"SELECT {', '.join(COLUMNS)} FROM gaiadr3.gaia_source "
        f"WHERE random_index >= {start} AND random_index < {stop} "
        f"AND {FILTER}"
    )
    response = session.get(
        TAP_URL,
        params={"REQUEST": "doQuery", "LANG": "ADQL", "FORMAT": "csv", "QUERY": query},
        timeout=180,
    )
    response.raise_for_status()
    if not response.text.startswith("source_id,"):
        raise ValueError(f"Gaia archive returned an unexpected response: {response.text[:200]}")
    frame = pd.read_csv(StringIO(response.text))
    if tuple(frame.columns) != COLUMNS:
        raise ValueError(f"Unexpected Gaia columns: {frame.columns.tolist()}")
    return frame


def archive_count(session: requests.Session) -> int:
    response = session.get(
        TAP_URL,
        params={
            "REQUEST": "doQuery", "LANG": "ADQL", "FORMAT": "csv",
            "QUERY": f"SELECT COUNT(*) AS n FROM gaiadr3.gaia_source WHERE random_index < {STOP} AND {FILTER}",
        },
        timeout=180,
    )
    response.raise_for_status()
    result = pd.read_csv(StringIO(response.text))
    if result.columns.tolist() != ["n"] or len(result) != 1:
        raise ValueError(f"Unexpected Gaia count response: {response.text[:200]}")
    return int(result["n"].iloc[0])


def build(output: Path) -> int:
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite {output}")
    writer = None
    completed = False
    count = 0
    try:
        with requests.Session() as session:
            for start in range(0, STOP, CHUNK):
                frame = download_chunk(session, start, start + CHUNK)
                if frame[["l", "b", "phot_g_mean_mag", "parallax"]].isna().any().any():
                    raise ValueError(f"Incomplete Gaia measurements in random_index [{start}, {start + CHUNK})")
                frame["galactic_longitude"] = ((frame.pop("l") + 180) % 360 - 180).astype("float32")
                frame["galactic_latitude"] = frame.pop("b").astype("float32")
                frame["absolute_g"] = (
                    frame["phot_g_mean_mag"] + 5 * np.log10(frame["parallax"]) - 10
                ).astype("float32")
                frame = frame[[
                    "source_id", "galactic_longitude", "galactic_latitude", "bp_rp", "absolute_g",
                    "phot_g_mean_mag", "parallax", "parallax_over_error",
                ]]
                frame = frame.astype({column: "float32" for column in frame if column != "source_id"})
                table = pa.Table.from_pandas(frame, preserve_index=False)
                if writer is None:
                    writer = pq.ParquetWriter(output, table.schema, compression="zstd")
                writer.write_table(table)
                count += len(frame)
                LOGGER.info("random_index [%s, %s): %s rows (%s total)", start, start + CHUNK, len(frame), count)
            expected = archive_count(session)
            if count != expected:
                raise ValueError(f"Gaia archive reports {expected} sources, but the extract contains {count}")
        completed = True
    finally:
        try:
            if writer is not None:
                writer.close()
        except Exception:
            completed = False
            raise
        finally:
            if not completed:
                output.unlink(missing_ok=True)
    return count


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="New Parquet file; existing files are never overwritten")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    LOGGER.info("Wrote %s Gaia DR3 rows to %s", build(args.output), args.output)
