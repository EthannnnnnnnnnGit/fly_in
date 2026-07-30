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
        if len(seperate) > 1:
            data, metadata = seperate
            metadata.strip("]")
        else:
            data = seperate
        try:
            data = self.check_data(data)
        except Exception as e:
            print(f"[{self.line}] {e}")

    def check_data():
        pass
