import os
import sys
from JackAnalyzer import JackAnalyzer


def main(input_path):
    if not os.path.exists(input_path):
        print("Please enter current filename or directory name")
        return

    if os.path.isfile(input_path):
        if os.path.splitext(input_path)[0] != "jack":
            print("Wrong file type, please enter jack file")
            return
        analyzer = JackAnalyzer(input_path)
        analyzer.process()

    if os.path.isdir(input_path):
        for f in os.listdir(input_path):
            if os.path.splitext(f)[1] == ".jack":
                filename = os.path.join(input_path, f)
                analyzer = JackAnalyzer(filename)
                analyzer.process()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Wrong number of arguments")
        sys.exit()
    main(sys.argv[1])
