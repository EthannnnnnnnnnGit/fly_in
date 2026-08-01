from src.parsing.parser import Parser
import sys


def main() -> None:
    parser = Parser()
    parser.get_data_files(sys.argv[1])


if __name__ == "__main__":
    main()
