# to fake delays in DummyRemoteFileProvider
import time

from pathlib import PurePosixPath

from panel.widgets import RemoteFileProvider


class DummyRemoteFileProvider(RemoteFileProvider):

    def __init__(self):
        super().__init__()

    async def ls(self, path:PurePosixPath):
        time.sleep(1)
        if str(path) == '/':
            return [f'dir_{l}' for l in 'ABCDEF' ], [f'file_{n}' for n in '123456' ]
        else:
            last_letter = path.parts[-1].replace("dir_", "")
            return [f'dir_{last_letter}{l}' for l in 'ABCDEF' ], [f'file_{last_letter + n}' for n in '123456' ]
