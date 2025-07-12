module CPU (clock, rst, forward_EN);
	input clock, rst, forward_EN;
	wire [31:0] PC_IF, inst_IF, PC_ID, inst_ID, PC_EXE, PC_MEM, reg1, reg2, reg1_EXE, reg2_EXE, ALU_Res, store_val, ALU_Res_MEM, store_val_MEM, data_out, ALU_Res_WB, data_out_WB, res_WB;
	wire [4:0] rs, rt, rd, sa, rd_EXE, sa_EXE;
	wire [5:0] opcode, funct, alu_inst, opcode_EXE, funct_EXE, alu_inst_EXE;
	wire read_mem_en, write_mem_en, wb_en, br_out, is_imm, is_shamt, is_imm_EXE, is_shamt_EXE;
	wire read_mem_en_EXE, write_mem_en_EXE, wb_en_EXE, br_out_EXE, read_mem_en_MEM, write_mem_en_MEM, wb_en_MEM, wb_en_WB, read_mem_en_WB;

	IF_Stage f_IF (clock, rst, PC_IF, inst_IF);
	IF_to_ID f_IF_to_ID (clock, rst, PC_IF, inst_IF, PC_ID, inst_ID);
	ID_Stage f_ID (inst_ID, opcode, rs, rt, rd, sa, funct, alu_inst, is_imm, is_shamt, read_mem_en, write_mem_en, wb_en, br_out);
	assign_reg f_assign_reg(clock, rst, rs, rt, rd, is_imm, res_WB, wb_en, reg1, reg2);
	ID_to_EXE f_ID_to_EXE (clock, rst, PC_ID, opcode, reg1, reg2, rd, sa, funct, alu_inst, is_imm, is_shamt, read_mem_en, write_mem_en, wb_en, br_out, PC_EXE, opcode_EXE, reg1_EXE, reg2_EXE, rd_EXE, sa_EXE, funct_EXE, alu_inst_EXE, is_imm_EXE, is_shamt_EXE, read_mem_en_EXE, write_mem_en_EXE, wb_en_EXE, br_out_EXE);
	EXE_Stage f_EXE (opcode_EXE, reg1_EXE, reg2_EXE, rd_EXE, sa_EXE, funct_EXE, alu_inst_EXE, is_imm_EXE, is_shamt_EXE, read_mem_en_EXE, write_mem_en_EXE, wb_en_EXE, br_out_EXE, ALU_Res, store_val);
	EXE_to_MEM f_EXE_to_MEM (clock, rst, PC_EXE, read_mem_en_EXE, write_mem_en_EXE, wb_en_EXE, ALU_Res, store_val, PC_MEM, read_mem_en_MEM, write_mem_en_MEM, wb_en_MEM, ALU_Res_MEM, store_val_MEM);
	MEMStage MEMStage (clock, rst, PC_MEM, read_mem_en_MEM, write_mem_en_MEM, ALU_Res_MEM, store_val_MEM, data_out);
	MEM_to_WB f_MEM_to_WB (clock, rst, wb_en_MEM, read_mem_en_MEM, ALU_Res_MEM, data_out, wb_en_WB, read_mem_en_WB, ALU_Res_WB, data_out_WB);
	WB_Stage f_WB (read_mem_en_WB, data_out_WB, ALU_Res_WB, res_WB);
endmodule

// Stage 1
module IF_Stage (clk, rst, PC, instruction);
input clk, rst, check;
output [31:0] PC, instruction;
wire [31:0] adder_out;
assign adder_out = PC+32'd4;
register f_reg (clk, rst, adder_out, PC);
InstructionRAM f_instructions (clk, rst, PC/4, instruction);
endmodule

module register (clk, rst, regIn, regOut);
input clk, rst;
input [31:0] regIn;
output reg [31:0] regOut;
always @ (posedge clk) begin
	if (rst==0) regOut <= regIn;
	else regOut <= 0;
end
endmodule

// Stage 1 to 2
module IF_to_ID (clk, reset, PC_in, instruction_in, PC_out, instruction_out);
input clk, reset, br_val;
input [31:0] PC_in, instruction_in;
output reg [31:0] PC_out, instruction_out;
always @(posedge clk) begin
	if (~reset) begin instruction_out <= instruction_in; PC_out <= PC_in; end
    else begin {PC_out, instruction_out} <= 0; end
end
endmodule

// Stage 2
module ID_Stage (instruction, opcode, rs, rt, rd, sa, funct, alu_inst, is_imm, is_shamt, read_mem_en, write_mem_en, wb_en, br_out);
input [31:0] instruction;
output [4:0] rs, rt, rd, sa;
output [5:0] opcode, funct, alu_inst;
output read_mem_en, write_mem_en, wb_en, br_out, is_imm, is_shamt;
wire br_en, br_cond, whether_imm, whether_shamt, sf;
get_values f_get_values(instruction[31:26], instruction[5:0],
  	alu_inst, br_en, br_cond, whether_imm, whether_shamt, sf, read_mem_en, write_mem_en, wb_en);
assign opcode = instruction[31:26];
assign rs = instruction[25:21];
assign rt = instruction[20:16];
assign rd = instruction[15:11];
assign sa = instruction[10:6];
assign funct = instruction[5:0];
assign is_imm = whether_imm;
assign is_shamt = whether_shamt;
assign br_out = br_en && br_cond;
endmodule

module get_values (opCode, func, alu_inst, brEn, brCond, whether_imm, whether_shamt, sf, read_mem_en, write_mem_en, wb_en);
input [5:0] opCode, func;
output reg brEn, brCond, whether_imm, whether_shamt, sf, read_mem_en, write_mem_en, wb_en;
output reg [5:0] alu_inst;
always @(*) begin
	{brEn, alu_inst, brCond, whether_imm, whether_shamt, sf, read_mem_en, write_mem_en, wb_en} <= 0;
	if (opCode == 6'b000000) begin
		case (func)
		6'b100000: begin alu_inst <= 6'b100000; wb_en <= 1; end //add
		6'b100001: begin alu_inst <= 6'b100000; wb_en <= 1; end //addu
		6'b100010: begin alu_inst <= 6'b100010; wb_en <= 1; end //sub
		6'b100011: begin alu_inst <= 6'b100010; wb_en <= 1; end //subu
		6'b100100: begin alu_inst <= 6'b100100; wb_en <= 1; end //and
		6'b100111: begin alu_inst <= 6'b100111; wb_en <= 1; end //nor
		6'b100101: begin alu_inst <= 6'b100101; wb_en <= 1; end //or
		6'b100110: begin alu_inst <= 6'b100110; wb_en <= 1; end //xor
		6'b000000: begin alu_inst <= 6'b000000; wb_en <= 1; whether_shamt <= 1; end //sll
		6'b000100: begin alu_inst <= 6'b000000; wb_en <= 1; end //sllv
		6'b000010: begin alu_inst <= 6'b000010; wb_en <= 1; whether_shamt <= 1; end //srl
		6'b000110: begin alu_inst <= 6'b000010; wb_en <= 1; end //srlv
		6'b000011: begin alu_inst <= 6'b000011; wb_en <= 1; whether_shamt <= 1; end //sra
		6'b000111: begin alu_inst <= 6'b000011; wb_en <= 1; end //srav
		default: {brEn, alu_inst, brCond, whether_imm, sf, read_mem_en, write_mem_en, wb_en} <= 0;
		endcase
	end
	else begin
		case (opCode)
		6'b001000: begin alu_inst <= 6'b100000; wb_en <= 1; whether_imm <= 1; end //addi
		6'b001001: begin alu_inst <= 6'b100000; wb_en <= 1; whether_imm <= 1; end //addiu
		6'b001100: begin alu_inst <= 6'b100100; wb_en <= 1; whether_imm <= 1; end //andi
		6'b001101: begin alu_inst <= 6'b100101; wb_en <= 1; whether_imm <= 1; end //ori
		6'b001110: begin alu_inst <= 6'b100110; wb_en <= 1; whether_imm <= 1; end //xori
		6'b100011: begin alu_inst <= 6'b100000; wb_en <= 1; whether_imm <= 1; read_mem_en <= 1; sf <= 1; end //lw
		6'b101011: begin alu_inst <= 6'b100000; whether_imm <= 1; write_mem_en <= 1; sf <= 1; end //sw
		6'b000100: begin alu_inst <= 6'b111111; whether_imm <= 1; brCond <= 1; brEn <= 1; end //beq
		6'b000101: begin alu_inst <= 6'b111111; whether_imm <= 1; brCond <= 1; brEn <= 1; sf <= 1; end //bne
		6'b000010: begin alu_inst <= 6'b111111; whether_imm <= 1; brCond <= 1; brEn <= 1; end //j
		6'b000011: begin alu_inst <= 6'b111111; whether_imm <= 1; brCond <= 1; brEn <= 1; end //jal
		default: {brEn, alu_inst, brCond, whether_imm, whether_shamt, sf, wb_en, read_mem_en, write_mem_en} <= 0;
		endcase
	end
end
endmodule

module assign_reg (clk, rst, rs, rt, rd, is_imm, write_val, write_en, reg1, reg2);
  input clk, rst, write_en, is_imm;
  input [4:0] rs, rt, rd;
  input [31:0] write_val;
  output [31:0] reg1, reg2;
  reg [31:0] regMem [0:4];
  integer i;
  always @ (negedge clk) begin
    if (rst) begin for (i = 0; i < 32; i = i + 1) regMem[i] <= 0; end
    else if (write_en) begin
	if (is_imm==0) regMem[rd] <= write_val;
	else regMem[rt] <= write_val;
	end
  end
  assign reg1 = (regMem[rs]);
  assign reg2 = (regMem[rt]);
endmodule

// Stage 2 to 3
module ID_to_EXE (clock, rst, PC_ID, opcode, reg1, reg2, rd, sa, funct, alu_inst, is_imm, is_shamt, read_mem_en, write_mem_en, wb_en, br_out,
	PC_EXE, opcode_EXE, reg1_EXE, reg2_EXE, rd_EXE, sa_EXE, funct_EXE, alu_inst_EXE, is_imm_EXE, is_shamt_EXE, read_mem_en_EXE, write_mem_en_EXE, wb_en_EXE, br_out_EXE);
input clock, rst;
input [31:0] reg1, reg2, PC_ID;
input [4:0] rd, sa;
input [5:0] opcode, funct, alu_inst;
input read_mem_en, write_mem_en, wb_en, br_out, is_imm, is_shamt;
output reg [31:0] reg1_EXE, reg2_EXE, PC_EXE;
output reg [4:0] rd_EXE, sa_EXE;
output reg [5:0] opcode_EXE, funct_EXE, alu_inst_EXE;
output reg read_mem_en_EXE, write_mem_en_EXE, wb_en_EXE, br_out_EXE, is_imm_EXE, is_shamt_EXE;
always @ (posedge clock) begin
    if (~rst) begin
		PC_EXE<=PC_ID; opcode_EXE<=opcode; reg1_EXE<=reg1; reg2_EXE<=reg2; rd_EXE<=rd; sa_EXE<=sa; funct_EXE<=funct; alu_inst_EXE<=alu_inst; 
		is_imm_EXE<=is_imm; is_shamt_EXE<=is_shamt; 
		read_mem_en_EXE<=read_mem_en; write_mem_en_EXE<=write_mem_en; wb_en_EXE<=wb_en; br_out_EXE<=br_out;
    end
    else begin {PC_EXE, opcode_EXE, reg1_EXE, reg2_EXE, rd_EXE, sa_EXE, funct_EXE, alu_inst_EXE, is_imm_EXE, is_shamt_EXE, read_mem_en_EXE, write_mem_en_EXE, wb_en_EXE, br_out_EXE} <= 0; end
end
endmodule

// Stage 3
module EXE_Stage (opcode_EXE, reg1_EXE, reg2_EXE, rd_EXE, sa_EXE, funct_EXE, alu_inst_EXE, is_imm_EXE, is_shamt_EXE, read_mem_en_EXE, write_mem_en_EXE, wb_en_EXE, br_out_EXE, res, store_val);
input [31:0] reg1_EXE, reg2_EXE;
input [4:0] rs_EXE, rt_EXE, rd_EXE, sa_EXE;
input [5:0] opcode_EXE, funct_EXE, alu_inst_EXE;
input read_mem_en_EXE, write_mem_en_EXE, wb_en_EXE, br_out_EXE, is_imm_EXE, is_shamt_EXE;
output [31:0] res, store_val;
wire [31:0] temp1, temp2;
assign temp1 = reg1_EXE;
assign temp2 = (is_imm_EXE)?{rd_EXE, sa_EXE, funct_EXE}:reg2_EXE;
assign store_val = {rd_EXE, sa_EXE, funct_EXE};
ALU f_ALU (temp1, temp2, alu_inst_EXE, res);
endmodule

module ALU (val1, val2, alu_inst, res);
input [31:0] val1, val2;
input [5:0] alu_inst;
output reg [31:0] res;
always @(*) begin
	case (alu_inst)
	6'b100000: res <= val1+val2; //add
	6'b100010: res <= val1-val2; //sub
	6'b100100: res <= val1&val2; //and
	6'b100111: res <= ~(val1|val2); //nor
	6'b100101: res <= val1|val2; //or
	6'b100110: res <= val1^val2; //xor
	6'b000000: res <= val1<<<val2; //sll
	6'b000010: res <= val1>>>val2; //srl
	6'b000011: res <= val1>>val2; //sra
	default: res <= 0;
	endcase
end
endmodule

// Stage 3 to 4
module EXE_to_MEM (clock, rst, PC_EXE, read_mem_en_EXE, write_mem_en_EXE, wb_en_EXE, ALU_Res, store_val, PC_MEM, read_mem_en_MEM, write_mem_en_MEM, wb_en_MEM, ALU_Res_MEM, store_val_MEM);
input clock, rst, read_mem_en_EXE, write_mem_en_EXE, wb_en_EXE;
input [31:0] ALU_Res, store_val, PC_EXE;
output reg read_mem_en_MEM, write_mem_en_MEM, wb_en_MEM;
output reg [31:0] ALU_Res_MEM, store_val_MEM, PC_MEM;
always @ (posedge clock) begin
    if (~rst) begin read_mem_en_MEM <= read_mem_en_EXE; write_mem_en_MEM <= write_mem_en_EXE; wb_en_MEM <= wb_en_EXE;
		ALU_Res_MEM <= ALU_Res; store_val_MEM <= store_val; PC_MEM<=PC_EXE; end
    else begin {PC_MEM, read_mem_en_MEM, write_mem_en_MEM, wb_en_MEM, ALU_Res_MEM, store_val_MEM} <= 0; end
  end
endmodule

// Stage 4
module MEMStage (clk, rst, PC_MEM, read_mem_en_MEM, write_mem_en_MEM, ALU_Res_MEM, store_val_MEM, data_out);
  input clk, rst, read_mem_en_MEM, write_mem_en_MEM;
  input [31:0] ALU_Res_MEM, store_val_MEM, PC_MEM;
  output [31:0] data_out;
  wire [64:0] temp;
  assign temp = {write_mem_en_MEM, PC_MEM, store_val_MEM};
  MainMemory dataMemory (
      .CLOCK(clk)
    , .RESET(rst)
    , .ENABLE(write_mem_en_MEM)
    , .FETCH_ADDRESS(store_val_MEM)
    , .EDIT_SERIAL(temp) // {1'b[is_edit], 32'b[write_add], 32'b[write_data]}
    , .DATA(data_out)
    );
endmodule

// Stage 4 to 5
module MEM_to_WB (clock, rst, wb_en_MEM, read_mem_en_MEM, ALU_Res_MEM, data_out, wb_en_WB, read_mem_en_WB, ALU_Res_WB, data_out_WB);
input clock, rst, wb_en_MEM, read_mem_en_MEM;
input [31:0] ALU_Res_MEM, data_out;
output reg wb_en_WB, read_mem_en_WB;
output reg [31:0] ALU_Res_WB, data_out_WB;
always @ (posedge clock) begin
    if (~rst) begin wb_en_WB<=wb_en_MEM; read_mem_en_WB<= read_mem_en_MEM; ALU_Res_WB<=ALU_Res_MEM; data_out_WB<=data_out; end
    else begin {wb_en_WB, read_mem_en_WB, ALU_Res_WB, data_out_WB} <= 0; end
end
endmodule

// Stage 5
module WB_Stage (read_mem_en_WB, data_out_WB, ALU_Res_WB, res_WB);
input read_mem_en_WB;
input [31:0] data_out_WB, ALU_Res_WB;
output [31:0] res_WB;
assign res_WB = (read_mem_en_WB)?data_out_WB:ALU_Res_WB;
endmodule