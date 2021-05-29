import os
import sys
from JackCompiler import JackCompiler


def main(input_path):
    if not os.path.exists(input_path):
        print("Please enter current filename or directory name")
        return

    if os.path.isfile(input_path):
        if os.path.splitext(input_path)[0] != "jack":
            print("Wrong file type, please enter jack file")
            return
        compiler = JackCompiler(input_path)
        compiler.process()

    if os.path.isdir(input_path):
        for f in os.listdir(input_path):
            if os.path.splitext(f)[1] == ".jack":
                filename = os.path.join(input_path, f)
                compiler = JackCompiler(filename)
                compiler.process()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Wrong number of arguments")
        sys.exit()
    main(sys.argv[1])
