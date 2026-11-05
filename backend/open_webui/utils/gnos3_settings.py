"""
Values of ours in the config table (`gnos3.*`), one row per key.

Upstream's Config has no knowledge of them; 3ff2c63645b8 copied the old ones over
from the single-row blob as they were. Config is imported when used, so tests with
fakes never touch the database.
"""


class StoredValue:
    def __init__(self, key: str, default):
        self.key = key
        self.default = default

    async def get(self):
        from open_webui.models.config import Config

        value = await Config.get(self.key, self.default)
        return self.default if value is None else value

    async def set(self, value) -> None:
        from open_webui.models.config import Config

        await Config.upsert({self.key: value})
