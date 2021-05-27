#include "include/symbol.h"

namespace nand2tetris{

SymbolTable::SymbolTable(){
    this->current_instruction_address = 0;
    this->current_data_address = 16;
    address_map = {
        {"SP", 0},
        {"LCL", 1},
        {"ARG", 2},
        {"THIS", 3},
        {"THAT", 4},
        {"SCREEN", 16384},
        {"KBD", 24576},
        {"R0", 0},
        {"R1", 1},
        {"R2", 2},
        {"R3", 3},
        {"R4", 4},
        {"R5", 5},
        {"R6", 6},
        {"R7", 7},
        {"R8", 8},
        {"R9", 9},
        {"R10", 10},
        {"R11", 11},
        {"R12", 12},
        {"R13", 13},
        {"R14", 14},
        {"R15", 15}
    };
}

SymbolTable::~SymbolTable(){
    address_map.clear();
}

void SymbolTable::AddEntry(std::string symbol, int address){
    this->address_map[symbol] = address;
    return;
}

bool SymbolTable::Contains(std::string symbol){
    return this->address_map.find(symbol) != this->address_map.end();
}

int SymbolTable::GetAddress(std::string symbol){
    return this->address_map[symbol];
}

int SymbolTable::GetInstructionAddress(){
    return this->current_instruction_address;
}

void SymbolTable::AddInstructionAddress(){
    this->current_instruction_address ++;
}

int SymbolTable::GetDataAddress(){
    return this->current_data_address;
}

void SymbolTable::AddDataAddress(){
    this->current_data_address++;
}

} //namespace name 