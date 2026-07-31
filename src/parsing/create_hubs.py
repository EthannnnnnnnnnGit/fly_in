from src.utils.hub import Hub


class CreateHub:
    def create_hubs(self, data: list[tuple[int, str]]):
        hubs = []
        for i, line in data:
            self.line = i
            valid_data = self.extract_data(line)
            if valid_data:
                hubs.append(Hub(*valid_data))
        return hubs

    def extract_data(self, line: str):
        seperate = line.split("[")
        try:
            data = self.check_data(seperate[0])
            if len(seperate > 1):
                metadata = self.check_metadata(seperate[1])
            else:
                metadata = ()
            return {data.update(metadata)}
        except Exception as e:
            print(f"[{self.line}] {e}")

    def check_data(self, data: str) -> dict:
        try:
            type, name, x, y = data.split()
        except Exception:
            print("jsp")

    def check_metadata(self, data: str) -> dict:
        pass
