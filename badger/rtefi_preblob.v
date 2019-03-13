// rtefi_blob.v is normally a preprocessed version of rtefi_preblob.v with
// definitions from the include file expressed/expanded.  That include file
// is itself machine-generated based on the desired clients.
//
// TL;DR: if this file is named rtefi_blob.v, it's probably a mistake to
// hand-edit it!
//
`include "rtefi_preblob.vh"
module rtefi_blob(
	// GMII Input (Rx)
	input rx_clk,
	input [7:0] rxd,
	input rx_dv,
	input rx_er,
	// GMII Output (Tx)
	input tx_clk,
	output [7:0] txd,
	output tx_en,
	// Configuration
	input enable_rx,
	input config_clk,
	input [3:0] config_a,
	input [7:0] config_d,
	input config_s,  // MAC/IP address write
	input config_p,  // UDP port number write
	// Debugging
	output ibadge_stb,
	output [7:0] ibadge_data,
	output obadge_stb,
	output [7:0] obadge_data,
	output xdomain_fault,
	// Pass-through to user modules
`BLOB_PORTS
	// Dumb stuff to get LEDs blinking
	output rx_mon,
	output tx_mon,
	// Simulation-only
	output in_use
);

parameter paw = 11;  // packet (memory) address width, nominal 11
parameter n_lat = 8;  // latency of client pipeline
// See comments in rtefi_center.v
parameter [31:0] ip = {8'd192, 8'd168, 8'd7, 8'd4};  // 192.168.7.4
parameter [47:0] mac = 48'h12555500012d;
parameter udp_port0 = 7;
parameter udp_port1 = 801;
parameter udp_port2 = 802;
parameter udp_port3 = 803;
parameter udp_port4 = 804;
parameter udp_port5 = 0;
parameter udp_port6 = 0;
parameter udp_port7 = 0;
`BLOB_PARAMS

wire [10:0] len_c;
wire [6:0] raw_l;
wire [6:0] raw_s;
wire [7:0] idata;
wire [7*8-1:0] mux_data_in;

rtefi_center #(.ip(ip), .mac(mac), .paw(paw), .n_lat(n_lat)) center(
	.rx_clk(rx_clk), .rxd(rxd),
	.rx_dv(rx_dv), .rx_er(rx_er),
	.tx_clk(tx_clk) , .txd(txd),
	.tx_en(tx_en),
	.enable_rx(enable_rx),
	.config_clk(config_clk), .config_s(config_s), .config_p(config_p),
	.config_a(config_a), .config_d(config_d),
	.len_c(len_c), .raw_l(raw_l), .raw_s(raw_s),
	.idata(idata), .mux_data_in(mux_data_in),
	.ibadge_stb(ibadge_stb), .ibadge_data(ibadge_data),
	.obadge_stb(obadge_stb), .obadge_data(obadge_data),
	.xdomain_fault(xdomain_fault),
	.rx_mon(rx_mon), .tx_mon(tx_mon), .in_use(in_use)
);

wire clk = tx_clk;
wire [7:0] odata_p7, odata_p6, odata_p5, odata_p4, odata_p3, odata_p2, odata_p1;
assign mux_data_in = {odata_p7, odata_p6, odata_p5, odata_p4, odata_p3, odata_p2, odata_p1};

`BLOB_INSTANCES

endmodule