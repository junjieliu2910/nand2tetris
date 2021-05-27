#include <string>
#include <map>


namespace nand2tetris{
class Code
{
private:
    std::map<std::string, std::string> dest_map;
    std::map<std::string, std::string> comp_map;
    std::map<std::string, std::string> jump_map; 
public:
    Code();
    ~Code();
    std::string DestinationCode(std::string dest);
    std::string ComputationCode(std::string comp);
    std::string JumpCode(std::string jump);
};

}// namespace name 
