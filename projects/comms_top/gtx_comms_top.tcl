###############################
# Configuration file for qgtx_wrap instances used in comms_top.v
# Quad GTX 0:
#    GTX0: Ethernet (1.25 Gbps)
#    GTX1: ChitChat (2.5 Gbps)
#    GTX2: -
#    GTX3: -
#
# Aux IP:
#    Ethernet MMCM
#
###############################

set GTX_CONFIG_DIR "../../fpga_family/gtx"
source $GTX_CONFIG_DIR/gtx_gen.tcl

# proc add_gtx_protocol {config_file quad_num gtx_num en8b10b enGTREFCLK1}

set quad 0
set gtx 0
set en8b10b 0
set enGTREFCLK1 0
add_gtx_protocol $GTX_CONFIG_DIR/gtx_ethernet.tcl $quad $gtx $en8b10b $enGTREFCLK1

set quad 0
set gtx 1
set en8b10b 1
set enGTREFCLK1 0
add_gtx_protocol $GTX_CONFIG_DIR/gtx_chitchat.tcl $quad $gtx $en8b10b $enGTREFCLK1

# proc add_aux_ip {ipname config_file module_name}
add_aux_ip clk_wiz $GTX_CONFIG_DIR/gtx_eth_clk.tcl gtx_eth_mmcm