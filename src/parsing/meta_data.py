from typing import Any


class ParseMetadata:
    def get_metadata(self, data: str) -> dict[str, Any]:
        data = data.split("[]")
