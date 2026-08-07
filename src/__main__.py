from src.parsing.parser import Parser
from src.algo.Dijkstra import Dijkstra
import sys


def main() -> None:
    parser = Parser()
    graph = parser.get_data_files(sys.argv[1])
    algo = Dijkstra(graph)
    print(algo.find_path())


if __name__ == "__main__":
    main()
