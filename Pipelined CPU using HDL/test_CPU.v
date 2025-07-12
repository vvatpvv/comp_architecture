`timescale 1ns/1ns
module testbench();
  reg clk, rst, forwarding_EN;
  integer i=0;
  CPU f_cpu(clk, rst, forwarding_EN);
  initial begin
    clk=1;
    repeat(130) begin
      #20 clk=~clk ;
      if (~clk) begin
      #20 $display("%b %b %h %h %h %h %h %h %h",
      f_cpu.inst_IF, f_cpu.opcode, f_cpu.alu_inst, f_cpu.read_mem_en, f_cpu.write_mem_en, 
      f_cpu.ALU_Res, f_cpu.store_val, f_cpu.data_out,
      f_cpu.res_WB
      ); end
      if (f_cpu.inst_ID==32'b11111111111111111111111111111111) i = 1;
      if (i>=1) i=i+1;
      if (i==10) #20 $display("stop");
    end
  end

  initial begin
    rst = 1;
    forwarding_EN = 0;
    #100
    rst = 0;
  end
endmodule
