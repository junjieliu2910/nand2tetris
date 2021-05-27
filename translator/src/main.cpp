#include <iostream>
#include <filesystem>

#include "Parser.h"
#include "CodeWriter.h"


void process(Parser& new_parser, CodeWriter& new_writer){
    while(new_parser.hasMoreCommand()){
        if(!new_parser.advance()){
            continue;
        }
        switch(new_parser.getCommandType()){
            case CommandType::C_ARITHMETIC:
                new_writer.writeArithmetic(new_parser.getOperation());
                break;
            case CommandType::C_PUSH:
            case CommandType::C_POP:{
                new_writer.writePushPop(new_parser.getOperation(), new_parser.getArg1(), new_parser.getArg2());
                break;
            }
            case CommandType::C_GOTO:{
                std::string label_name;
                if(new_parser.getInsideFunction()){
                    label_name = new_parser.getFunctionName() + "$" + new_parser.getArg1();
                }else{
                    label_name = new_parser.getArg1();
                }
                new_writer.writeGoto(label_name);
                break;
            }
            case CommandType::C_IF:{
                std::string label_name;
                if(new_parser.getInsideFunction()){
                    label_name = new_parser.getFunctionName() + "$" + new_parser.getArg1();
                }else{
                    label_name = new_parser.getArg1();
                }
                new_writer.writeIf(label_name);
                break; 
            }
            case CommandType::C_LABEL:{
                std::string label_name;
                if(new_parser.getInsideFunction()){
                    label_name = new_parser.getFunctionName() + "$" + new_parser.getArg1();
                }else{
                    label_name = new_parser.getArg1();
                }
                new_writer.writeLabel(label_name);
                break; 
            }
            case CommandType::C_FUNCTION:{
                new_writer.writeFunction(new_parser.getArg1(), new_parser.getArg2());
                break;
            }
            case CommandType::C_CALL:{
                new_writer.writeCall(new_parser.getArg1(), new_parser.getArg2());
                break;
            }
            case CommandType::C_RETURN:
                new_writer.writeReturn();
                break;
            default:
                break;
        }
    }
}

int main(int argc, char** argv){
    if(argc != 2){
        std::cerr << "Please enter the filename without options" << std::endl;
        exit(1);
    }
    const std::string path_string(argv[1]);
    const std::filesystem::path path(path_string);
    std::error_code ec; 
    if(std::filesystem::is_directory(path, ec)){
        std::string output_filename = path_string + path.parent_path().filename().string() + ".asm";
        CodeWriter new_writer(output_filename);
        for (const auto & entry : std::filesystem::directory_iterator(path)){
            if(entry.is_regular_file()){
                std::string vm_filename = entry.path().string();
                Parser temp(vm_filename);
                new_writer.setFileName(vm_filename);
                process(temp, new_writer);
            }
        }
    }
    if(ec){
        std::cerr << "Error in is_directory: " << ec.message();
    }
    if(std::filesystem::is_regular_file(path, ec)){
        std::string input_filename(argv[1]);
        // check extensin 
        if(path.extension().string() != "vm"){
            std::cout << "Wrong file type, please enter a VM file" << std::endl;
            exit(3);
        }
        Parser new_parser(input_filename);
        std::string output_file_name = input_filename.substr(0, input_filename.find_last_of('.')) + std::string(".asm");
        CodeWriter new_writer(output_file_name);
        new_writer.setFileName(input_filename);
        process(new_parser, new_writer);
    }
    if(ec){
        std::cerr << "Error in is_regular_file: " << ec.message();
    }
    return 0;
}

