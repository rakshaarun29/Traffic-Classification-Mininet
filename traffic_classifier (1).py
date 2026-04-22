"""
Traffic Classification System - SDN Project
Ryu OpenFlow Controller (OpenFlow 1.3)
Classifies TCP, UDP, ICMP traffic and maintains per-protocol statistics.
"""

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4, tcp, udp, icmp
from ryu.lib.packet import ether_types


class TrafficClassifier(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(TrafficClassifier, self).__init__(*args, **kwargs)
        self.mac_to_port = {}

        self.stats = {
            'TCP': 0,
            'UDP': 0,
            'ICMP': 0,
            'TOTAL': 0
        }

        self.logger.info("Traffic Classification System STARTED")

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto

        # Send all packets to controller
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]

        self.add_flow(datapath, 0, match, actions)

        self.logger.info("Switch connected: dpid=%s", datapath.id)

    def add_flow(self, datapath, priority, match, actions,
                 idle_timeout=0, hard_timeout=0):

        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto

        inst = [parser.OFPInstructionActions(
            ofproto.OFPIT_APPLY_ACTIONS, actions)]

        mod = parser.OFPFlowMod(
            datapath=datapath,
            priority=priority,
            idle_timeout=idle_timeout,
            hard_timeout=hard_timeout,
            match=match,
            instructions=inst
        )

        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):

        msg = ev.msg
        datapath = msg.datapath
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)

        if eth is None:
            return

        # Ignore LLDP and IPv6
        if eth.ethertype == ether_types.ETH_TYPE_LLDP or eth.ethertype == 0x86DD:
            return

        src = eth.src
        dst = eth.dst
        dpid = datapath.id

        # MAC learning
        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][src] = in_port

        # ---------------- ARP HANDLING (CRITICAL) ----------------
        if eth.ethertype == 0x0806:  # ARP
            if dst in self.mac_to_port[dpid]:
                out_port = self.mac_to_port[dpid][dst]
            else:
                out_port = ofproto.OFPP_FLOOD

            actions = [parser.OFPActionOutput(out_port)]

            out = parser.OFPPacketOut(
                datapath=datapath,
                buffer_id=ofproto.OFP_NO_BUFFER,
                in_port=in_port,
                actions=actions,
                data=msg.data
            )

            datapath.send_msg(out)
            return
        # --------------------------------------------------------

        ip_pkt = pkt.get_protocol(ipv4.ipv4)

        # Ignore non-IP packets
        if not ip_pkt:
            return

        # -------- PROTOCOL CLASSIFICATION --------
        if pkt.get_protocol(tcp.tcp):
            protocol = 'TCP'
        elif pkt.get_protocol(udp.udp):
            protocol = 'UDP'
        elif pkt.get_protocol(icmp.icmp):
            protocol = 'ICMP'
        else:
            return
        # ----------------------------------------

        # Update stats
        self.stats[protocol] += 1
        self.stats['TOTAL'] += 1

        # Logging
        self.logger.info(
            "[CLASSIFY] %s | %s -> %s | TCP:%d UDP:%d ICMP:%d TOTAL:%d",
            protocol,
            src,
            dst,
            self.stats['TCP'],
            self.stats['UDP'],
            self.stats['ICMP'],
            self.stats['TOTAL']
        )

        # Forwarding
        if dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][dst]
        else:
            out_port = ofproto.OFPP_FLOOD

        actions = [parser.OFPActionOutput(out_port)]

        out = parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=ofproto.OFP_NO_BUFFER,
            in_port=in_port,
            actions=actions,
            data=msg.data
        )

        datapath.send_msg(out)