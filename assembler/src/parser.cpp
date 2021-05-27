#include <exception>
#include <algorithm>
#include <bitset>

#include "include/parser.h"

namespace nand2tetris{

Parser::Parser(std::string input_file){
    if(input_file.substr(input_file.find_last_of('.')+1)!="asm"){
        std::cout << "Wrong file type" << std::endl;
        exit(0);
    }
    this->file_name = input_file;
    // this->in_file.exceptions(std::ifstream::failbit | std::ifstream::badbit);
    try{
        this->in_file.open(this->file_name);
    }
    catch(const std::system_error& e){
        std::cerr << e.code().message() << std::endl;
    }
    std::string output_file_name = input_file.substr(0, input_file.find_last_of('.')) + std::string(".hack");
    this->out_file.open(output_file_name);
    if(!this->out_file.is_open()){
        std::cout << "Output file open fails" << std::endl;
        exit(1);
    }
    this->code_dict = Code();
    this->symbol_table = SymbolTable();
}

Parser::~Parser(){
    this->in_file.close();
    this->out_file.close();
}


bool Parser::HasMoreCommand(){
    int len = this->in_file.tellg();
    std::string dummy;
    std::getline(this->in_file, dummy);
    bool result = !this->in_file.eof();
    this->in_file.seekg(len, std::ios_base::beg);
    return result; 
}

void Parser::Advance(){
    std::string command;
    std::getline(this->in_file, command);
    command = this->Preprocess(command);
    if(command.empty()){
        return;
    }
    if(command[0] == '@'){
        // A command
        std::string address_str = command.substr(1);
        int address_dec;
        if(this->ContainSymbol(address_str)){
            if(this->symbol_table.Contains(address_str)){
                address_dec = this->symbol_table.GetAddress(address_str);
            }else{
                address_dec = this->symbol_table.GetDataAddress();
                this->symbol_table.AddDataAddress();
                this->symbol_table.AddEntry(address_str, address_dec);
            }
        }else{
            address_dec = std::stoi(address_str);
        }
        std::string machine_code = std::bitset<16>(address_dec).to_string();
        this->out_file << machine_code << std::endl;
    }else if(command[0] == '('){
        // L command
        // std::string symbol = this->Symbol(command);
        // int address_dec = this->symbol_table.GetInstructionAddress();
        // this->symbol_table.AddEntry(symbol, address_dec);
        return;
    }else{
        // C command
        std::string machine_code = "111";
        std::string dest_code = this->code_dict.DestinationCode(this->Destination(command));
        std::string comp_code = this->code_dict.ComputationCode(this->Computation(command));
        std::string jump_code = this->code_dict.JumpCode(this->Jump(command));
        machine_code = machine_code + comp_code + dest_code + jump_code;
        this->out_file << machine_code << std::endl;
    }
}

void Parser::BuildInstructionTable(){
    std::ifstream temp_steam(this->file_name);
    std::string command;
    while(std::getline(temp_steam, command)){
        command = this->Preprocess(command);
        if(command.empty()){
            continue;
        }
        if(command[0] == '('){
            std::string symbol = this->Symbol(command);
            this->symbol_table.AddEntry(symbol, this->symbol_table.GetInstructionAddress());
        }else{
            this->symbol_table.AddInstructionAddress();
        }
    } 
    temp_steam.close();
}

std::string Parser::Preprocess(std::string command){
    // Remove all space 
    command.erase(std::remove(command.begin(), command.end(), '\n'), command.end());
    command.erase(std::remove(command.begin(), command.end(), '\r'), command.end());
    command.erase(std::remove(command.begin(), command.end(), ' '), command.end());
    // Remove comment
    auto position = command.find("//");
    if(position != std::string::npos){
        return command.substr(0, position); 
    }
    return command;
}


std::string Parser::Destination(std::string command) {
    if(command.find('=')!=std::string::npos){
        std::string dest_str = command.substr(0, command.find_first_of('='));
        return dest_str;
    }else{
        return std::string("null");
    }
}

std::string Parser::Computation(std::string command){
    if(command.find('=')!=std::string::npos){
        return command.substr(command.find_first_of('=')+1);
    }else{
        return command.substr(0, command.find_first_of(';'));
    }
}

std::string Parser::Jump(std::string command){
    if(command.find(';')!=std::string::npos){
        std::string jump_str = command.substr(command.find_first_of(';')+1);
        return jump_str;
    }else{
        return std::string("null");
    }
}

bool Parser::ContainSymbol(std::string command){
    return !std::all_of(command.begin(), command.end(), ::isdigit);
}

std::string Parser::Symbol(std::string command){
    // return symbol only for L-command 
    return command.substr(1, command.length()-2);
}

}// namespace name