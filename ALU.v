module ALU(instruction, regA, regB, result, flags);
    input[31:0] instruction, regA, regB;
    output[31:0] result;
    output[2:0] flags;
    wire zero, negative, overflow;
    wire[31:0] result_add, result_addi, result_addu, result_addiu,
        result_sub, result_subu,
        result_and, result_andi, result_nor, result_or, result_ori, result_xor, result_xori,
        result_beq, result_bne, result_slt, result_slti, result_sltiu, result_sltu,
        resultsub_slt, resultsub_slti, resultsub_sltiu, resultsub_sltu,
        result_lw, result_sw,
        result_sll, result_sllv, result_srl, result_srlv, result_sra, result_srav;
    wire overflow_add, overflow_addi, overflow_sub, zero_beq, zero_bne;
    wire[15:0] imm;
    wire[5:0] opcode, func;
    wire[4:0] shamt;

    // Step 1: Parsing the instruction
    assign opcode = instruction[31:26];
    assign func = instruction[5:0];
    assign shamt = instruction[10:6];
    assign imm = instruction[15:0];

    // Step 2: Performing all the available modules
    M_add   f_add   (regA, regB,    result_add,    overflow_add);
    M_addi  f_addi  (regA, imm,     result_addi,   overflow_addi);
    M_addu  f_addu  (regA, regB,    result_addu);
    M_addiu f_addiu (regA, imm,     result_addiu);
    M_sub   f_sub   (regA, regB,    result_sub,    overflow_sub);
    M_subu  f_subu  (regA, regB,    result_subu);
    M_and   f_and   (regA, regB,    result_and);
    M_andi  f_andi  (regA, imm,     result_andi);
    M_nor   f_nor   (regA, regB,    result_nor);
    M_or    f_or    (regA, regB,    result_or);
    M_ori   f_ori   (regA, imm,     result_ori);
    M_xor   f_xor   (regA, regB,    result_xor);
    M_xori  f_xori  (regA, imm,     result_xori);
    M_beq   f_beq   (regA, regB, imm, result_beq,   zero_beq);
    M_bne   f_bne   (regA, regB, imm, result_bne,   zero_bne);
    M_slt   f_slt   (regA, regB,    result_slt, resultsub_slt);
    M_slti  f_slti  (regA, imm,     result_slti, resultsub_slti);
    M_sltiu f_sltiu (regA, imm,     result_sltiu, resultsub_sltiu);
    M_sltu  f_sltu  (regA, regB,    result_sltu, resultsub_sltu);
    M_lw    f_lw    (regA, regB, imm, result_lw);
    M_sw    f_sw    (regA, regB, imm, result_sw);
    M_sll   f_sll   (regA, shamt,   result_sll);
    M_sllv  f_sllv  (regA, regB,    result_sllv);
    M_srl   f_srl   (regA, shamt,   result_srl);
    M_srlv  f_srlv  (regA, regB,    result_srlv);
    M_sra   f_sra   (regA, shamt,   result_sra);
    M_srav  f_srav  (regA, regB,    result_srav);

    // Step 3: Getting the appropriate value of result and status of flags
    wire[31:0] opcode5, opcode4, opcode3, opcode2, opcode1, opcode0;
    wire[31:0] func5, func4, func3, func2, func1, func0;
    assign opcode5 = {32{opcode[5]}};
    assign opcode4 = {32{opcode[4]}};
    assign opcode3 = {32{opcode[3]}};
    assign opcode2 = {32{opcode[2]}};
    assign opcode1 = {32{opcode[1]}};
    assign opcode0 = {32{opcode[0]}};
    assign func5 = {32{func[5]}};
    assign func4 = {32{func[4]}};
    assign func3 = {32{func[3]}};
    assign func2 = {32{func[2]}};
    assign func1 = {32{func[1]}};
    assign func0 = {32{func[0]}};
    
    assign result = 
    // add: opcode 000000, func 100000
    ~opcode5&~opcode4&~opcode3&~opcode2&~opcode1&~opcode0&func5&~func4&~func3&~func2&~func1&~func0&result_add|
    // addi: opcode 001000
    ~opcode5&~opcode4&opcode3&~opcode2&~opcode1&~opcode0&result_addi|
    // addu: opcode 000000, func 100001
    ~opcode5&~opcode4&~opcode3&~opcode2&~opcode1&~opcode0&func5&~func4&~func3&~func2&~func1&func0&result_addu|
    // addiu: opcode 001001
    ~opcode5&~opcode4&opcode3&~opcode2&~opcode1&opcode0&result_addiu|
    // sub: opcode 000000, func 100010
    ~opcode5&~opcode4&~opcode3&~opcode2&~opcode1&~opcode0&func5&~func4&~func3&~func2&func1&~func0&result_sub|
    // subu: opcode 000000, func 100011
    ~opcode5&~opcode4&~opcode3&~opcode2&~opcode1&~opcode0&func5&~func4&~func3&~func2&func1&func0&result_subu|
    // and: opcode 000000, func 100100
    ~opcode5&~opcode4&~opcode3&~opcode2&~opcode1&~opcode0&func5&~func4&~func3&func2&~func1&~func0&result_and|
    // andi: opcode 001100
    ~opcode5&~opcode4&opcode3&opcode2&~opcode1&~opcode0&result_andi|
    // nor: opcode 000000, func 100111
    ~opcode5&~opcode4&~opcode3&~opcode2&~opcode1&~opcode0&func5&~func4&~func3&func2&func1&func0&result_nor|
    // or: opcode 000000, func 100101
    ~opcode5&~opcode4&~opcode3&~opcode2&~opcode1&~opcode0&func5&~func4&~func3&func2&~func1&func0&result_or|        
    // ori: opcode 001101
    ~opcode5&~opcode4&opcode3&opcode2&~opcode1&opcode0&result_ori|
    // xor: opcode 000000, func 100110
    ~opcode5&~opcode4&~opcode3&~opcode2&~opcode1&~opcode0&func5&~func4&~func3&func2&func1&~func0&result_xor|
    // ori: opcode 001110
    ~opcode5&~opcode4&opcode3&opcode2&opcode1&~opcode0&result_xori|
    // beq: opcode 000100
    ~opcode5&~opcode4&~opcode3&opcode2&~opcode1&~opcode0&result_beq|
    // bne: opcode 000101
    ~opcode5&~opcode4&~opcode3&opcode2&~opcode1&opcode0&result_bne|
    // slt: opcode 000000, func 101010
    ~opcode5&~opcode4&~opcode3&~opcode2&~opcode1&~opcode0&func5&~func4&func3&~func2&func1&~func0&resultsub_slt|        
    // slti: opcode 001010
    ~opcode5&~opcode4&opcode3&~opcode2&opcode1&~opcode0&resultsub_slti|
    // sltiu: opcode 001011
    ~opcode5&~opcode4&opcode3&~opcode2&opcode1&opcode0&resultsub_sltiu|
    // sltu: opcode 000000, func 101011
    ~opcode5&~opcode4&~opcode3&~opcode2&~opcode1&~opcode0&func5&~func4&func3&~func2&func1&func0&resultsub_sltu|
    // lw: opcode 100011
    opcode5&~opcode4&~opcode3&~opcode2&opcode1&opcode0&result_lw|
    // lw: opcode 101011
    opcode5&~opcode4&opcode3&~opcode2&opcode1&opcode0&result_sw|
    // sll: opcode 000000, func 000000
    ~opcode5&~opcode4&~opcode3&~opcode2&~opcode1&~opcode0&~func5&~func4&~func3&~func2&~func1&~func0&result_sll|
    // sllv: opcode 000000, func 000100
    ~opcode5&~opcode4&~opcode3&~opcode2&~opcode1&~opcode0&~func5&~func4&~func3&func2&~func1&~func0&result_sllv|
    // srl: opcode 000000, func 000010
    ~opcode5&~opcode4&~opcode3&~opcode2&~opcode1&~opcode0&~func5&~func4&~func3&~func2&func1&~func0&result_srl|
    // srlv: opcode 000000, func 000110
    ~opcode5&~opcode4&~opcode3&~opcode2&~opcode1&~opcode0&~func5&~func4&~func3&func2&func1&~func0&result_srlv|
    // sra: opcode 000000, func 000011
    ~opcode5&~opcode4&~opcode3&~opcode2&~opcode1&~opcode0&~func5&~func4&~func3&~func2&func1&func0&result_sra|
    // srav: opcode 000000, func 000111
    ~opcode5&~opcode4&~opcode3&~opcode2&~opcode1&~opcode0&~func5&~func4&~func3&func2&func1&func0&result_srav;

    // zero only consider beq, bne
    assign zero=~opcode[5]&~opcode[4]&~opcode[3]&opcode[2]&~opcode[1]&~opcode[0]&~zero_beq|
    ~opcode[5]&~opcode[4]&~opcode[3]&opcode[2]&~opcode[1]&opcode[0]&~zero_bne;

    // negative only consider slt, slti, sltiu, sltu
    assign negative=
    ~opcode[5]&~opcode[4]&~opcode[3]&~opcode[2]&~opcode[1]&~opcode[0]&func[5]&~func[4]&func[3]&~func[2]&func[1]&~func[0]&result_slt[0]|        
    ~opcode[5]&~opcode[4]&opcode[3]&~opcode[2]&opcode[1]&~opcode[0]&result_slti[0]|
    ~opcode[5]&~opcode[4]&opcode[3]&~opcode[2]&opcode[1]&opcode[0]&result_sltiu[0]|
    ~opcode[5]&~opcode[4]&~opcode[3]&~opcode[2]&~opcode[1]&~opcode[0]&func[5]&~func[4]&func[3]&~func[2]&func[1]&func[0]&result_sltu[0];      
    
    // overflow only consider add, addi, sub
    assign overflow = 
    ~opcode[5]&~opcode[4]&~opcode[3]&~opcode[2]&~opcode[1]&~opcode[0]&func[5]&~func[4]&~func[3]&~func[2]&~func[1]&~func[0]&overflow_add|
    ~opcode[5]&~opcode[4]&opcode[3]&~opcode[2]&~opcode[1]&~opcode[0]&overflow_addi|
    ~opcode[5]&~opcode[4]&~opcode[3]&~opcode[2]&~opcode[1]&~opcode[0]&func[5]&~func[4]&~func[3]&~func[2]&func[1]&~func[0]&overflow_sub;
    
    assign flags[2] = zero;
    assign flags[1] = negative;
    assign flags[0] = overflow;
endmodule

module M_and(regA, regB, result_and);
    input [31:0] regA, regB;
    output [31:0] result_and;
    output overflow;
    assign result_and = regA & regB;
endmodule

module M_andi(regA, imm, result_andi);
    input [31:0] regA;
    input [15:0] imm;
    output [31:0] result_andi;
    wire [31:0] temp;
    assign temp = {16'b0000000000000000, imm};
    assign result_andi = regA & temp;
endmodule

module M_nor(regA, regB, result_nor);
    input [31:0] regA, regB;
    output [31:0] result_nor;
    assign result_nor = ~(regA|regB);
endmodule

module M_or(regA, regB, result_or);
    input [31:0] regA, regB;
    output [31:0] result_or;
    assign result_or = regA|regB;
endmodule

module M_ori(regA, imm, result_ori);
    input [31:0] regA;
    input [15:0] imm;
    output [31:0] result_ori;
    wire [31:0] temp;
    assign temp = {16'b0000000000000000, imm};
    assign result_ori = regA|temp;
endmodule

module M_xor(regA, regB, result_xor);
    input [31:0] regA, regB;
    output [31:0] result_xor;
    assign result_xor = regA^regB;
endmodule

module M_xori(regA, imm, result_xori);
    input [31:0] regA;
    input [15:0] imm;
    output [31:0] result_xori;
    wire [31:0] temp;
    assign temp = {16'b0000000000000000, imm};
    assign result_xori = regA^temp;
endmodule

module M_sll(regA, shamt, result_sll);
    input [31:0] regA;
    input [4:0] shamt;
    output [31:0] result_sll;
    assign result_sll = regA << shamt;
endmodule

module M_sllv(regA, regB, result_sllv);
    input [31:0] regA, regB;
    output [31:0] result_sllv;
    assign result_sllv = regA << regB;
endmodule

module M_srl(regA, shamt, result_srl);
    input [31:0] regA;
    input [4:0] shamt;
    output [31:0] result_srl;
    assign result_srl = regA >> shamt;
endmodule

module M_srlv(regA, regB, result_srlv);
    input [31:0] regA, regB;
    output [31:0] result_srlv;
    assign result_srlv = regA >> regB;
endmodule

module M_sra(regA, shamt, result_sra);
    input [31:0] regA;
    input [4:0] shamt;
    output [31:0] result_sra;
    assign result_sra = $signed(regA) >>> shamt;
endmodule

module M_srav(regA, regB, result_srav);
    input [31:0] regA, regB;
    output [31:0] result_srav;
    assign result_srav = $signed(regA) >>> regB;
endmodule

module compare_values(valA, valB, compare_result_prev, compare_result_after);
    input valA, valB;
    input [2:0] compare_result_prev;
    output [2:0] compare_result_after;
    assign compare_result_after[2] = valA&~valB | (valA&valB|~valA&~valB)&compare_result_prev[2];
    assign compare_result_after[1] = (valA&valB|~valA&~valB) & compare_result_prev[1];
    assign compare_result_after[0] = ~valA&valB | (valA&valB|~valA&~valB)&compare_result_prev[0];
endmodule

module compare_not_signed(regA, regB, compare_result);
    input [31:0] regA, regB;
    output [2:0] compare_result;
    wire [2:0] compare_result_init,
        compare_result_1, compare_result_2, compare_result_3, compare_result_4,
        compare_result_5, compare_result_6, compare_result_7, compare_result_8,
        compare_result_9, compare_result_10, compare_result_11, compare_result_12,
        compare_result_13, compare_result_14, compare_result_15, compare_result_16,
        compare_result_17, compare_result_18, compare_result_19, compare_result_20,
        compare_result_21, compare_result_22, compare_result_23, compare_result_24,
        compare_result_25, compare_result_26, compare_result_27, compare_result_28, 
        compare_result_29, compare_result_30, compare_result_31;
    assign compare_result_init[2] = 0;
    assign compare_result_init[1] = 1;
    assign compare_result_init[0] = 0;
    compare_values val0(regA[0], regB[0], compare_result_init, compare_result_1);
    compare_values val1(regA[1], regB[1], compare_result_1, compare_result_2);
    compare_values val2(regA[2], regB[2], compare_result_2, compare_result_3);
    compare_values val3(regA[3], regB[3], compare_result_3, compare_result_4);
    compare_values val4(regA[4], regB[4], compare_result_4, compare_result_5);
    compare_values val5(regA[5], regB[5], compare_result_5, compare_result_6);
    compare_values val6(regA[6], regB[6], compare_result_6, compare_result_7);
    compare_values val7(regA[7], regB[7], compare_result_7, compare_result_8);
    compare_values val8(regA[8], regB[8], compare_result_8, compare_result_9);
    compare_values val9(regA[9], regB[9], compare_result_9, compare_result_10);
    compare_values val10(regA[10], regB[10], compare_result_10, compare_result_11);
    compare_values val11(regA[11], regB[11], compare_result_11, compare_result_12);
    compare_values val12(regA[12], regB[12], compare_result_12, compare_result_13);
    compare_values val13(regA[13], regB[13], compare_result_13, compare_result_14);
    compare_values val14(regA[14], regB[14], compare_result_14, compare_result_15);
    compare_values val15(regA[15], regB[15], compare_result_15, compare_result_16);
    compare_values val16(regA[16], regB[16], compare_result_16, compare_result_17);
    compare_values val17(regA[17], regB[17], compare_result_17, compare_result_18);
    compare_values val18(regA[18], regB[18], compare_result_18, compare_result_19);
    compare_values val19(regA[19], regB[19], compare_result_19, compare_result_20);
    compare_values val20(regA[20], regB[20], compare_result_20, compare_result_21);
    compare_values val21(regA[21], regB[21], compare_result_21, compare_result_22);
    compare_values val22(regA[22], regB[22], compare_result_22, compare_result_23);
    compare_values val23(regA[23], regB[23], compare_result_23, compare_result_24);
    compare_values val24(regA[24], regB[24], compare_result_24, compare_result_25);
    compare_values val25(regA[25], regB[25], compare_result_25, compare_result_26);
    compare_values val26(regA[26], regB[26], compare_result_26, compare_result_27);
    compare_values val27(regA[27], regB[27], compare_result_27, compare_result_28);
    compare_values val28(regA[28], regB[28], compare_result_28, compare_result_29);
    compare_values val29(regA[29], regB[29], compare_result_29, compare_result_30);
    compare_values val30(regA[30], regB[30], compare_result_30, compare_result_31);
    compare_values val31(regA[31], regB[31], compare_result_31, compare_result);
endmodule

module compare_signed(regA, regB, compare_result);
    input [31:0] regA, regB;
    output [2:0] compare_result;
    wire [31:0] regA1, regB1;
    wire [2:0] temp_compare_result;
    assign regA1 = {1'b0, regA[30:0]};
    assign regB1 = {1'b0, regB[30:0]};
    compare_not_signed f_compare_1(regA1, regB1, temp_compare_result);
    assign compare_result[2] = ~regA[31]&regB[31] | ~regA[31]&~regB[31]&temp_compare_result[2] | regA[31]&regB[31]&temp_compare_result[2];
    assign compare_result[1] = ~regA[31]&~regB[31]&temp_compare_result[1] | regA[31]&regB[31]&temp_compare_result[1];
    assign compare_result[0] = regA[31]&~regB[31] | ~regA[31]&~regB[31]&temp_compare_result[0] | regA[31]&regB[31]&temp_compare_result[0];
endmodule

module M_slt(regA, regB, result_slt, resultsub_slt);
    input [31:0] regA, regB;
    output [31:0] result_slt, resultsub_slt;
    wire [2:0] compare_result;
    compare_signed f_slt_compare(regA, regB, compare_result);
    assign result_slt = (32'b1) & compare_result[0];
    M_subu slt_sub(regA, regB, resultsub_slt);
endmodule

module M_slti(regA, imm, result_slti, resultsub_slti);
    input [31:0] regA;
    input [15:0] imm;
    output [31:0] result_slti, resultsub_slti;
    wire [2:0] compare_result;
    wire [31:0] c;
    assign c = {{16{imm[15]}}, imm};
    compare_signed f_slti_compare(regA, c, compare_result);
    assign result_slti = (32'b1) & compare_result[0];
    M_subu slti_sub(regA, c, resultsub_slti);
endmodule

module M_sltu(regA, regB, result_sltu, resultsub_sltu);
    input [31:0] regA, regB;
    output [31:0] result_sltu, resultsub_sltu;
    wire [2:0] compare_result;
    compare_not_signed f_sltu_compare(regA, regB, compare_result);
    assign result_sltu = (32'b1) & compare_result[0];
    M_subu sltu_sub(regA, regB, resultsub_sltu);
endmodule

module M_sltiu(regA, imm, result_sltiu, resultsub_sltiu);
    input [31:0] regA;
    input [15:0] imm;
    output [31:0] result_sltiu, resultsub_sltiu;
    wire [2:0] compare_result;
    wire [31:0] c;
    assign c = {{16{imm[15]}}, imm};
    compare_not_signed f_sltiu_compare(regA, c, compare_result);
    assign result_sltiu = (32'b1) & compare_result[0];
    M_subu sltiu_sub(regA, c, resultsub_sltiu);
endmodule

module M_beq(regA, regB, imm, result_beq, zero_beq);
    input [31:0] regA, regB;
    input [15:0] imm;
    output [31:0] result_beq;
    output zero_beq;
    wire [2:0] compare_result;
    compare_not_signed f_beq_compare(regA, regB, compare_result);
    assign result_beq = {1'b0, imm} & {32{(compare_result[1])}};
    assign zero_beq = compare_result[1];
endmodule

module M_bne(regA, regB, imm, result_bne, zero_bne);
    input [31:0] regA, regB;
    input [15:0] imm;
    output [31:0] result_bne;
    output zero_bne;
    wire [2:0] compare_result;
    compare_not_signed f_bne_compare(regA, regB, compare_result);
    assign result_bne = {1'b0, imm} & {32{(~compare_result[1])}};
    assign zero_bne = ~compare_result[1];
endmodule

module M_lw(regA, regB, imm, result_lw);
    input [31:0] regA, regB;
    input [15:0] imm;
    output [31:0] result_lw;
    wire temp;
    assign temp = regA[0]|imm[0];
    assign result_lw = ({32{(~temp)}} & regA) | ({32{(temp)}} & regB);
endmodule

module M_sw(regA, regB, imm, result_sw);
    input [31:0] regA, regB;
    input [15:0] imm;
    output [31:0] result_sw;
    wire adr;
    assign adr = regA[0]|imm[0];
    assign result_sw = regB;
endmodule

module add_values(v1, v2, c, sum, carry);
    input v1, v2, c;
    output sum, carry;
    assign sum = ((~v1)&(~v2)&c)|((~v1)&v2&(~c))|(v1&(~v2)&(~c))|(v1&v2&c);
    assign carry = ((~v1)&v2&c)|(v1&(~v2)&c)|(v1&v2);
endmodule

module M_add(regA, regB, result_add, overflow_add);
    input[31:0] regA, regB;
    output[31:0] result_add;
    output overflow_add;
    wire [31:0] c;
    add_values v0(regA[0], regB[0], 1'b0, result_add[0], c[0]);
    add_values v1(regA[1], regB[1], c[0], result_add[1], c[1]);
    add_values v2(regA[2], regB[2], c[1], result_add[2], c[2]);
    add_values v3(regA[3], regB[3], c[2], result_add[3], c[3]);
    add_values v4(regA[4], regB[4], c[3], result_add[4], c[4]);
    add_values v5(regA[5], regB[5], c[4], result_add[5], c[5]);
    add_values v6(regA[6], regB[6], c[5], result_add[6], c[6]);
    add_values v7(regA[7], regB[7], c[6], result_add[7], c[7]);
    add_values v8(regA[8], regB[8], c[7], result_add[8], c[8]);
    add_values v9(regA[9], regB[9], c[8], result_add[9], c[9]);
    add_values v10(regA[10], regB[10], c[9], result_add[10], c[10]);
    add_values v11(regA[11], regB[11], c[10], result_add[11], c[11]);
    add_values v12(regA[12], regB[12], c[11], result_add[12], c[12]);
    add_values v13(regA[13], regB[13], c[12], result_add[13], c[13]);
    add_values v14(regA[14], regB[14], c[13], result_add[14], c[14]);
    add_values v15(regA[15], regB[15], c[14], result_add[15], c[15]);
    add_values v16(regA[16], regB[16], c[15], result_add[16], c[16]);
    add_values v17(regA[17], regB[17], c[16], result_add[17], c[17]);
    add_values v18(regA[18], regB[18], c[17], result_add[18], c[18]);
    add_values v19(regA[19], regB[19], c[18], result_add[19], c[19]);
    add_values v20(regA[20], regB[20], c[19], result_add[20], c[20]);
    add_values v21(regA[21], regB[21], c[20], result_add[21], c[21]);
    add_values v22(regA[22], regB[22], c[21], result_add[22], c[22]);
    add_values v23(regA[23], regB[23], c[22], result_add[23], c[23]);
    add_values v24(regA[24], regB[24], c[23], result_add[24], c[24]);
    add_values v25(regA[25], regB[25], c[24], result_add[25], c[25]);
    add_values v26(regA[26], regB[26], c[25], result_add[26], c[26]);
    add_values v27(regA[27], regB[27], c[26], result_add[27], c[27]);
    add_values v28(regA[28], regB[28], c[27], result_add[28], c[28]);
    add_values v29(regA[29], regB[29], c[28], result_add[29], c[29]);
    add_values v30(regA[30], regB[30], c[29], result_add[30], c[30]);
    add_values v31(regA[31], regB[31], c[30], result_add[31], c[31]);
    assign overflow_add = (regA[31]&regB[31]&(~result_add[31])) | ((~regA[31])&(~regB[31])&result_add[31]);
endmodule

module M_addu(regA, regB, result_addu);
    input[31:0] regA, regB;
    output[31:0] result_addu;
    output overflow_addu;
    wire temp;
    M_add f_add_1(regA, regB, result_addu, temp);
endmodule

module M_addi(regA, imm, result_addi, overflow_addi);
    input [31:0] regA;
    input [15:0] imm;
    output [31:0] result_addi;
    wire [31:0] c;
    assign c = {{16{imm[15]}}, imm};
    output overflow_addi;
    M_add f_add_2(regA, c, result_addi, overflow_addi);
endmodule

module M_addiu(regA, imm, result_addiu);
    input [31:0] regA;
    input [15:0] imm;
    output [31:0] result_addiu;
    wire [31:0] c;
    assign c = {{16{imm[15]}}, imm};
    wire temp;
    M_add f_add_3(regA, c, result_addiu, temp);
endmodule

module M_sub(regA, regB, result_sub, overflow_sub);
    input [31:0] regA, regB;
    output [31:0] result_sub;
    output temp, overflow_sub;
    wire [31:0] c;
    M_add f_add_4(~regB, 32'b1, c, temp);
    M_add f_add_5(regA, c, result_sub, overflow_sub);
endmodule

module M_subu(regA, regB, result_subu);
    input [31:0] regA, regB;
    output [31:0] result_subu;
    wire temp;
    M_sub f_sub_1(regA, regB, result_subu, temp);
endmodule
