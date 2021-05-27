#include <string> 
#include <iostream>
#include <fstream>

#include "code.h"
#include "symbol.h"


namespace nand2tetris{
// enum class command_type {a_command=0, c_command, l_command};

class Parser{
private:
    std::string file_name;
    std::ifstream in_file;
    std::ofstream out_file; 
    Code code_dict;
    SymbolTable symbol_table;
public:
    Parser(std::string input_file);
    ~Parser();
    bool HasMoreCommand();
    void Advance();
    void BuildInstructionTable();
    static std::string Destination(std::string command);
    static std::string Computation(std::string command);
    static std::string Jump(std::string command);
    static std::string Preprocess(std::string command);
    static bool ContainSymbol(std::string);
    static std::string Symbol(std::string command);
};

}// namespace name


