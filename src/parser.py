class Parser:
    def read_file(self, filename: str) -> None:
        try:
            with open(filename, "r") as f:
                lines = f.readlines()
        except OSError:
            print("An error as occured while attempting to reach files data")
        else:
            self.lines = lines

    def check_files():
        pass

