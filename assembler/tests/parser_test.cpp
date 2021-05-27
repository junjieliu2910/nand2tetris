#include "gtest/gtest.h"
#include "include/parser.h"

namespace nand2tetris{
TEST(ParserTest, DestinationTest){
    std::string output = Parser::Destination("D=D+1");
    EXPECT_EQ(output, "D");
    output = Parser::Destination("AMD=1");
    EXPECT_EQ(output, "AMD");
    output = Parser::Destination("D;JMP");
    EXPECT_EQ(output, "null");
}

TEST(ParserTest, ComputationTest){
    std::string output = Parser::Computation("D=D+1");
    EXPECT_EQ(output, "D+1");
    output = Parser::Computation("D+1;JMP");
    EXPECT_EQ(output, "D+1");
    output = Parser::Computation("D=!A");
    EXPECT_EQ(output, "!A");
}

TEST(ParserTest, JumpTest){
    std::string output = Parser::Jump("D=D+1");
    EXPECT_EQ(output, "null");
    output = Parser::Jump("!D;JMP");
    EXPECT_EQ(output, "JMP");
}

TEST(ParserTest, PreprocessTest){
    std::string output = Parser::Preprocess("// this is a comment");
    EXPECT_EQ(output, "");
    output = Parser::Preprocess("D=D+1// this is a test");
    EXPECT_EQ(output, "D=D+1");
    output = Parser::Preprocess("D; JMP  // this is a test");
    EXPECT_EQ(output, "D;JMP");
    output = Parser::Preprocess("");
    EXPECT_EQ(output, "");
    output = Parser::Preprocess("@10086 // coomend fsa");
    EXPECT_EQ(output, "@10086");
}

TEST(ParserTest, ContainSymbolTest){
    ASSERT_FALSE(Parser::ContainSymbol("12342"));
    ASSERT_FALSE(Parser::ContainSymbol("000"));
    ASSERT_FALSE(Parser::ContainSymbol("3451"));
    ASSERT_TRUE(Parser::ContainSymbol("LOOP"));
    ASSERT_TRUE(Parser::ContainSymbol("P2345"));
    ASSERT_TRUE(Parser::ContainSymbol("sum"));
}

TEST(ParserTest, SymbolTest){
    std::string output = Parser::Symbol("(LOOP)");
    EXPECT_EQ(output, "LOOP");
    output = Parser::Symbol("(sum)");
    EXPECT_EQ(output, "sum");
    output = Parser::Symbol("(R0)");
    EXPECT_EQ(output, "R0");
}

} //namesapce name 