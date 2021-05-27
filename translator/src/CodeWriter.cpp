#include <string>
#include <fstream> 
#include <iostream>
#include <filesystem>

#include "CodeWriter.h"

CodeWriter::CodeWriter(std::string filename){
    this->filename = filename;
    this->out_file.open(filename);
    this->binary_compare_operation_count = 0;
    this->function_call_count = 0;
    this->writeBootstrap();
}

CodeWriter::~CodeWriter(){
    this->close();
}

void CodeWriter::setFileName(std::string filename){
    this->vm_filename = filename;
}

std::string CodeWriter::getFileName(){
    return this->vm_filename;
}

void CodeWriter::close(){
    this->out_file.close();
}

void CodeWriter::writeArithmetic(std::string command){
    std::string assemble;
    if(command == "add"){
        assemble = "@SP\nAM=M-1\nD=M\nA=A-1\nM=D+M\n";
    }else if(command == "sub"){
        assemble = "@SP\nAM=M-1\nD=M\nA=A-1\nM=M-D\n";
    }else if(command == "and"){
        assemble = "@SP\nAM=M-1\nD=M\nA=A-1\nM=D&M\n";
    }else if(command == "or"){
        assemble = "@SP\nAM=M-1\nD=M\nA=A-1\nM=M|D\n";
    }else if(command == "neg"){
        assemble = "@SP\nA=M-1\nM=-M\n";
    }else if(command == "not"){
        assemble = "@SP\nA=M-1\nM=!M\n";
    }else if(command == "eq"){
        std::string compare_temp = std::to_string(this->binary_compare_operation_count++);
        assemble = "@SP\nAM=M-1\nD=M\nA=A-1\nD=M-D\n";
        assemble += "@eqTrue" + compare_temp + "\nD;JEQ\n";
        assemble += "@SP\nA=M-1\nM=0\n@eqEnd" + compare_temp + "\nD;JMP\n";
        assemble += "(eqTrue" + compare_temp + ")\n@SP\nA=M-1\nM=-1\n(eqEnd" + compare_temp + ")\n";
    }else if(command == "gt"){
        std::string compare_temp = std::to_string(this->binary_compare_operation_count++);
        assemble = "@SP\nAM=M-1\nD=M\nA=A-1\nD=M-D\n";
        assemble += "@eqTrue" + compare_temp + "\nD;JGT\n";
        assemble += "@SP\nA=M-1\nM=0\n@eqEnd" + compare_temp + "\nD;JMP\n";
        assemble += "(eqTrue" + compare_temp + ")\n@SP\nA=M-1\nM=-1\n(eqEnd" + compare_temp + ")\n";
    }else if(command == "lt"){
        std::string compare_temp = std::to_string(this->binary_compare_operation_count++);
        assemble = "@SP\nAM=M-1\nD=M\nA=A-1\nD=M-D\n";
        assemble += "@eqTrue" + compare_temp + "\nD;JLT\n";
        assemble += "@SP\nA=M-1\nM=0\n@eqEnd" + compare_temp + "\nD;JMP\n";
        assemble += "(eqTrue" + compare_temp + ")\n@SP\nA=M-1\nM=-1\n(eqEnd" + compare_temp + ")\n";
    }else{
        std::cout << "wrong arithmetic operation" << std::endl;
        exit(1);
    }
    this->out_file << assemble;
}

void CodeWriter::writePushPop(std::string command, std::string segment, int index){
    std::string assemble;
    if(command == "push"){
        if(segment == "argument"){
            assemble = "@ARG\nA=M\n";
            for(int i = 0; i < index; ++i){
                assemble += "A=A+1\n";
            }
            assemble += "D=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n";
        }else if(segment == "local"){
            assemble = "@LCL\nA=M\n";
            for(int i = 0; i < index; ++i){
                assemble += "A=A+1\n";
            }
            assemble += "D=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n";
        }else if(segment == "static"){
            const std::filesystem::path p(this->getFileName());
            std::string file_stem = p.stem().string();
            assemble = "@" + file_stem + "." + std::to_string(index) + "\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n"; 
        }else if(segment == "constant"){
            assemble = "@" + std::to_string(index) + "\nD=A\n";
            assemble += "@SP\nA=M\nM=D\n@SP\nM=M+1\n";
        }else if(segment == "this"){
            assemble = "@THIS\nA=M\n";
            for(int i = 0; i < index; ++i){
                assemble += "A=A+1\n";
            }
            assemble += "D=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n";
        }else if(segment == "that"){
            assemble = "@THAT\nA=M\n";
            for(int i = 0; i < index; ++i){
                assemble += "A=A+1\n";
            }
            assemble += "D=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n";
        }else if(segment == "pointer"){
            if(index == 0){
                assemble = "@3\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n";
            }else if(index == 1){
                assemble = "@4\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n";
            }
        }else if(segment == "temp"){
            int address = 5 + index;
            assemble = "@" + std::to_string(address) + "\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n";
        }else{
            std::cout << "writePushPop error, Wrong segment type" << std::endl;
            exit(4);
        }
    }else if(command == "pop"){
        if(segment == "argument"){
            assemble = "@SP\nAM=M-1\nD=M\n";
            assemble += "@ARG\nA=M\n";
            for(int i = 0; i < index; ++i){
                assemble += "A=A+1\n";
            }
            assemble += "M=D\n";
        }else if(segment == "local"){
            assemble = "@SP\nAM=M-1\nD=M\n";
            assemble += "@LCL\nA=M\n";
            for(int i = 0; i < index; ++i){
                assemble += "A=A+1\n";
            }
            assemble += "M=D\n";
        }else if(segment == "static"){
            const std::filesystem::path p(this->getFileName());
            std::string file_stem = p.stem().string();
            assemble = "@SP\nAM=M-1\nD=M\n";
            assemble += "@" + file_stem + "." + std::to_string(index) + "\nM=D\n";
        }else if(segment == "this"){
            assemble = "@SP\nAM=M-1\nD=M\n";
            assemble += "@THIS\nA=M\n";
            for(int i = 0; i < index; ++i){
                assemble += "A=A+1\n";
            }
            assemble += "M=D\n";
        }else if(segment == "that"){
            assemble = "@SP\nAM=M-1\nD=M\n";
            assemble += "@THAT\nA=M\n";
            for(int i = 0; i < index; ++i){
                assemble += "A=A+1\n";
            }
            assemble += "M=D\n";
        }else if(segment == "pointer"){
            if(index == 0){
                assemble = "@SP\nAM=M-1\nD=M\n@3\nM=D\n";
            }else if(index == 1){
                assemble = "@SP\nAM=M-1\nD=M\n@4\nM=D\n";
            }
        }else if(segment == "temp"){
            int address = 5 + index;
            assemble = "@SP\nAM=M-1\nD=M\n@" + std::to_string(address) + "\nM=D\n";
        }else{
            std::cout << "writePushPop error, Wrong segment type" << std::endl;
            exit(4);
        }
    }else{
        std::cout << "writePushPop error, Wrong commend type" << std::endl;
        exit(3);
    }
    this->out_file << assemble;
}

void CodeWriter::writeLabel(std::string label){
    std::string assemble = "(" + label + ")\n";
    this->out_file << assemble; 
}

void CodeWriter::writeGoto(std::string label){
    std::string assemble = "@" + label + "\nD;JMP\n";
    this->out_file << assemble; 
}

void CodeWriter::writeIf(std::string label){
    std::string compare_temp = std::to_string(this->binary_compare_operation_count++);
    std::string assemble = "@SP\nAM=M-1\nD=M\n@IfZero" + compare_temp +"\nD;JEQ\n@" + label +"\nD;JMP\n(IfZero"+ compare_temp +")\n";
    this->out_file << assemble;
}

void CodeWriter::writeFunction(std::string function_name, int num_lcls){
    std::string assemble = "(" + function_name + ")\n";
    this->out_file << assemble;
    for(int i = 0; i < num_lcls; ++i){
        writePushPop("push", "constant", 0);
    }
}

void CodeWriter::writeCall(std::string function_name, int num_args){
    std::string assemble; 
   
    // push return-address 
    assemble = "@" + function_name + ".return" + std::to_string(this->function_call_count) + "\n" + "D=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n";
    // push LCL 
    assemble += "@LCL\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n";
    // push ARG
    assemble += "@ARG\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n";
    // push THIS
    assemble += "@THIS\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n";
    // push THAT 
    assemble += "@THAT\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n";
    // renew ARG
    assemble += "@SP\nD=M\n";
    for(int i = 0; i < num_args + 5; ++i){
        assemble += "D=D-1\n";
    }
    assemble += "@ARG\nM=D\n";
    // renew LCL 
    assemble += "@SP\nD=M\n@LCL\nM=D\n";
    assemble += "@" + function_name +"\nD;JMP\n";
    assemble += "(" + function_name + ".return" + std::to_string(this->function_call_count) + ")\n";
    this->function_call_count ++;
    this->out_file << assemble;
}

void CodeWriter::writeReturn(){
    // R13 = LCL 
    std::string assemble = "@LCL\nD=M\n@R13\nM=D\n";
    // RET = *(FRAME-5)
    assemble += "@R13\nD=M-1\nD=D-1\nD=D-1\nD=D-1\nD=D-1\nA=D\nD=M\n@R14\nM=D\n";
    // *ARG = *(SP-1) (return value)
    assemble += "@SP\nA=M-1\nD=M\n@ARG\nA=M\nM=D\n";
    // SP = ARG + 1
    assemble += "@ARG\nM=M+1\nD=M\n@SP\nM=D\n";
    // THAT = *(FRAME-1)
    assemble += "@R13\nAM=M-1\nD=M\n@THAT\nM=D\n";
    // THIS = *(FRAME-2)
    assemble += "@R13\nAM=M-1\nD=M\n@THIS\nM=D\n";
    // ARG = *(FRAME-3)
    assemble += "@R13\nAM=M-1\nD=M\n@ARG\nM=D\n";
    // LCL = *(FRAME-4)
    assemble += "@R13\nAM=M-1\nD=M\n@LCL\nM=D\n";
    // Return 
    assemble += "@R14\nA=M\nD;JMP\n";
    this->out_file << assemble;
}

void CodeWriter::writeBootstrap(){
    std::string assemble = "@256\nD=A\n@SP\nM=D\n";
    this->out_file << assemble;
    this->writeCall("Sys.init", 0);
}