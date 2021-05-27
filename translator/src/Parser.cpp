#include <sstream>
#include <algorithm>

#include "Parser.h"

const std::unordered_set<std::string> Parser::arithmetic_set = { "add", "sub", "neg", "eq", "gt", "lt", "and", "or", "not"};


Parser::Parser(std::string filename): filename(filename) {
    this->in_file.open(filename);
}

Parser::~Parser(){
    this->in_file.close();
}

bool Parser::hasMoreCommand(){
    int len = this->in_file.tellg();
    std::string dummy;
    std::getline(this->in_file, dummy);
    bool result = !this->in_file.eof();
    this->in_file.seekg(len, std::ios_base::beg);
    return result;  
}

bool Parser::advance(){
    std::string current_command;
    std::getline(this->in_file, current_command);
    current_command = this->Preprocess(current_command);
    std::vector<std::string> words = this->splitCommand(current_command);
    if(words.size() == 0){
        return false; // empty line 
    }
    CommandType type = this->commandType(words[0]);
    if(words.size() == 1){
        if(type == CommandType::C_ARITHMETIC || type == CommandType::C_RETURN){
            this->type = type;
            this->command = words[0];
        }
    }else if(words.size() == 2){
        if(type == CommandType::C_LABEL || type ==CommandType::C_IF || type == CommandType::C_GOTO){
            this->type = type;
            this->command = words[0];
            this->arg1 = words[1];
        }
    }else if(words.size() == 3){
        if(type == CommandType::C_PUSH || type == CommandType::C_POP || type == CommandType::C_FUNCTION || type == CommandType::C_CALL){
            this->type = type; 
            this->command = words[0];
            this->arg1 = words[1];
            this->arg2 = std::stoi(words[2]); 
            // For label and goto inside a function 
            if(type == CommandType::C_FUNCTION){
                this->function_stack.push_back(words[1]);
            }
            if(type == CommandType::C_RETURN){
                this->function_stack.pop_back();
            }
        }
    }
    return true;
}

CommandType Parser::commandType(std::string command){
    // Process the command after preprocessing 
    if(Parser::arithmetic_set.find(command) != Parser::arithmetic_set.end()){
        return CommandType::C_ARITHMETIC;
    }else if(command == "push"){
        return CommandType::C_PUSH;
    }else if(command == "pop"){
        return CommandType::C_POP;
    }else if(command == "label"){
        return CommandType::C_LABEL;
    }else if(command == "goto"){
        return CommandType::C_GOTO;
    }else if(command == "if-goto"){
        return CommandType::C_IF;
    }else if(command == "function"){
        return CommandType::C_FUNCTION;
    }else if(command == "call"){
        return CommandType::C_CALL;
    }else if(command == "return"){
        return CommandType::C_RETURN;
    }
    return CommandType::C_ERROR;
}

std::vector<std::string> Parser::splitCommand(std::string command){
    std::istringstream in(command);
    std::vector<std::string> v;
    std::string temp;
    while(in >> temp){
        v.push_back(temp);
    } 
    return v;
}

std::string Parser::Preprocess(std::string command){
    // remove newline and carriage return  
    command.erase(std::remove(command.begin(), command.end(), '\n'), command.end());
    command.erase(std::remove(command.begin(), command.end(), '\r'), command.end());
    // remove comment 
    auto position = command.find("//");
    if(position != std::string::npos){
        command = command.substr(0, position);
    }
    return command;
}


std::string Parser::getOperation(){
    return this->command;
}

std::string Parser::getArg1(){
    return this->arg1;
}

int Parser::getArg2(){
    return this->arg2;
}

CommandType Parser::getCommandType(){
    return this->type;
}

bool Parser::getInsideFunction(){
    return !this->function_stack.empty();
}

std::string Parser::getFunctionName(){
    return this->function_stack.back();
}

std::string Parser::getFileName(){
    return this->filename;
}