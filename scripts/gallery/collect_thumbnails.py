import asyncio
import pathlib

import aiohttp

THUMBNAIL_URL = 'https://assets.holoviz.org/panel'
GALLERY_DIR = pathlib.Path(__file__).parent.parent.parent / 'examples' / 'gallery'
THUMBNAIL_DIR = GALLERY_DIR / 'thumbnails'
GALLERY_ITEMS = GALLERY_DIR.glob('*.ipynb')
THUMBNAIL_DIR.mkdir(exist_ok=True)

async def download(path, name, session):
    filename = f'{name[:-6].lower()}.png'
    url = f'{THUMBNAIL_URL}/{path}/{filename}'
    async with session.get(url) as response:
        if response.content_type != 'image/png':
            return
        with open(THUMBNAIL_DIR / filename, "wb") as f:
            f.write(await response.read())

async def download_all():
    async with aiohttp.ClientSession() as session:
        await asyncio.gather(
            *[download(item.parent.name, item.name, session) for item in GALLERY_ITEMS]
        )

asyncio.run(download_all())
