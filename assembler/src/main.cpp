#include <iostream>
#include "include/parser.h"

int main(int argc, char** argv){
    if(argc != 2){
        std::cout << "Please enter the filename without options" << std::endl;
        return 1;
    }
    std::string filename = std::string(argv[1]);
    nand2tetris::Parser parser(filename);
    parser.BuildInstructionTable();
    while(parser.HasMoreCommand()){
        parser.Advance();
    }
    return 0;
}
