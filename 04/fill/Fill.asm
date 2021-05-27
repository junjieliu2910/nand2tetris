// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.
(CHECK)
    @SCREEN 
    D=A 
    @i
    M=D  // i = SCREEN 
    @KBD 
    D=M
    @BLACK
    D;JGT
    @CLEAR
    0;JMP
(BLACK)
    D=0
    D=!D 
    @i 
    A=M
    M=D
    @i 
    MD=M+1 
    @KBD
    D=D-A
    @CHECK
    D;JGE 
    @BLACK
    0;JMP 
(CLEAR)
    @i 
    A=M
    M=0
    @i 
    MD=M+1 
    @KBD
    D=D-A
    @CHECK
    D;JGE 
    @CLEAR
    0;JMP 