#include <string> 
#include <iostream>
#include <fstream>
#include <vector>
#include <unordered_set>

enum class CommandType {C_ARITHMETIC=0, C_PUSH, C_POP, C_LABEL, C_GOTO, C_IF, C_FUNCTION, C_RETURN, C_CALL, C_ERROR};

class Parser{
private:
    static const std::unordered_set<std::string> arithmetic_set;
    const std::string filename;
    std::ifstream in_file; 
    CommandType type; 
    std::string command;
    std::string arg1;
    int arg2;
    // Variable for function, call, and return 
    std::vector<std::string> function_stack;

public:
    // Maintains the current state of the command

    Parser(std::string filename);
    ~Parser();
    bool hasMoreCommand();
    bool advance();
    static CommandType commandType(std::string command); 
    CommandType getCommandType();
    std::string getOperation();
    std::string getArg1();
    int getArg2();
    bool getInsideFunction();
    std::string getFunctionName();
    std::string getFileName();
    static std::vector<std::string> splitCommand(std::string command);

    // Helper function 
    static std::string Preprocess(std::string command);  
};

