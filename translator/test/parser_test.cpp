#include "gtest/gtest.h"
#include "Parser.h"
#include "CodeWriter.h"



TEST(Parser_test, commandTypeTest){
    CommandType output = Parser::commandType("add");
    EXPECT_EQ(output, CommandType::C_ARITHMETIC);
    output = Parser::commandType("sub");
    EXPECT_EQ(output, CommandType::C_ARITHMETIC);
    output = Parser::commandType("push");
    EXPECT_EQ(output, CommandType::C_PUSH);
    output = Parser::commandType("pop");
    EXPECT_EQ(output, CommandType::C_POP);
}


TEST(Parser_test, splitCommandTest){
    std::vector<std::string> output = Parser::splitCommand("    ");
    EXPECT_EQ(output.size(), 0);
    output = Parser::splitCommand("  push argument 0  ");
    EXPECT_EQ(output.size(), 3);
    EXPECT_EQ(output[0], "push");
    EXPECT_EQ(output[1], "argument");
    EXPECT_EQ(output[2], "0");
    output = Parser::splitCommand("  pop  local  2");
    EXPECT_EQ(output.size(), 3);
    EXPECT_EQ(output[0], "pop");
    EXPECT_EQ(output[1], "local");
    EXPECT_EQ(output[2], "2");
    output = Parser::splitCommand("   add ");
    EXPECT_EQ(output.size(), 1);
    EXPECT_EQ(output[0], "add");
}
