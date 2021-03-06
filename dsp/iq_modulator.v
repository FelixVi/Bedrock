`timescale 1ns / 1ns

module iq_modulator (
	input clk,
	input signed [WIDTH-1:0] sin,
	input signed [WIDTH-1:0] cos,
	output signed [WIDTH-1:0] d_out,
	input signed [WIDTH-1:0] ampi,
	input signed [WIDTH-1:0] ampq
);
// note that negative full-scale amplitude is considered invalid
// also plan that abs(ampi+ampq*i) < 1

// Universal definition; note: old and new are msb numbers, not bit widths.
`define SAT(x,old,new) ((~|x[old:new] | &x[old:new]) ? x[new:0] : {x[old],{new{~x[old]}}})
parameter WIDTH=16;
// TODO: Add testbench - possibly based on phshift
reg signed [2*WIDTH-1:0] p1=0, p2=0;  // product registers
wire signed [WIDTH:0] p1s = p1[2*WIDTH-2:WIDTH-2];
wire signed [WIDTH:0] p2s = p2[2*WIDTH-2:WIDTH-2];
wire signed [WIDTH+1:0] sum = p1s + p2s + 1;  // one lsb guard, with rounding
reg signed [WIDTH:0] d3=0;
always @(posedge clk) begin
	p1 <= ampi * cos;
	p2 <= ampq * sin;
	d3 <= `SAT(sum, WIDTH+1, WIDTH);
end
assign d_out = d3[WIDTH:1];

endmodule
