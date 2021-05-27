#include <string>
#include <fstream> 

class CodeWriter
{
private:
    /* data */
    std::string filename;
    std::string vm_filename;
    std::ofstream out_file;
    int binary_compare_operation_count;
    int function_call_count;

public:
    CodeWriter(std::string filename);
    ~CodeWriter();
    void setFileName(std::string filename);
    std::string getFileName();
    void writeArithmetic(std::string command);
    void writePushPop(std::string command, std::string segment, int index);
    void writeInit();
    void writeLabel(std::string label);
    void writeGoto(std::string label);
    void writeIf(std::string label);
    void writeFunction(std::string function_name, int num_lcls);
    void writeCall(std::string function_name, int num_args);
    void writeReturn();
    void writeBootstrap();
    void close();
    
};

