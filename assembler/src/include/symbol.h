#include <string> 
#include <map>

namespace nand2tetris{

class SymbolTable{
private:
    /* data */
    int current_instruction_address;
    int current_data_address;
    std::map<std::string, int> address_map; 
public:
    SymbolTable();
    ~SymbolTable();
    void AddEntry(std::string symbol, int address);
    bool Contains(std::string);
    int GetAddress(std::string);
    int GetInstructionAddress();
    void AddInstructionAddress();
    int GetDataAddress();
    void AddDataAddress();
};
} //namesapce name 

