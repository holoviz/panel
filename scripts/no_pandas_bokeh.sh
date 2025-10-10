#!/usr/bin/env bash
set -euo pipefail

# Find installed Bokeh package path
BOKEH_DIR=$(python -c "import bokeh, pathlib; print(pathlib.Path(bokeh.__file__).resolve().parent)")
SITE_PKGS=$(dirname "$BOKEH_DIR")

# Create a temporary diff file
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIFF_FILE="$SCRIPT_DIR/no_pandas_bokeh.diff"

echo "🧭 Located Bokeh at: $BOKEH_DIR"
cd "$SITE_PKGS"
patch -p2 <"$DIFF_FILE"
echo "✅ Patch applied successfully."
