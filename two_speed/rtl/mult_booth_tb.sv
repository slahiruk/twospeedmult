`timescale 1ns / 100ps
module mult_booth_tb;

  localparam DATA_WIDTH = 32;

  logic [2*DATA_WIDTH-1:0] res;

  logic                    clk    ;
  logic [  DATA_WIDTH-1:0] i_a    ;
  logic [  DATA_WIDTH-1:0] i_b    ;
  logic                    i_valid;
  logic                    o_valid;
  logic [2*DATA_WIDTH-1:0] o_z    ;

  mult_booth DUT (
    .clk    (clk    ),
    .i_a    (i_a    ),
    .i_b    (i_b    ),
    .i_valid(i_valid),
    .o_valid(o_valid),
    .o_c    (o_z    )
  );


  initial begin
    clk = 0;
    forever begin
      #1.8 clk = ~clk;
    end
  end

  initial begin
    runTest(0, 0);
	 runTest(0, 1);
	 runTest(1, 0);
	 runTest(342, 25);
	 $finish();
  end

  task runTest (
  input logic [DATA_WIDTH-1:0] a,
  input logic [DATA_WIDTH-1:0] b
  );
      @(negedge clk);
		i_a = a;
		i_b = b;
      i_valid = 1;
      res = $signed(i_a*i_b);
      @(posedge clk);
      i_valid = 0;
      @(posedge clk);
      @(posedge clk);
      while (!o_valid) @(posedge clk);
      assert (o_z == res) $display("OK.");
  endtask


endmodule
