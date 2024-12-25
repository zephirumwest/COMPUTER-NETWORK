from scapy.all import srp, Ether, ARP, conf
import netifaces, psutil
from threading import Thread


class ARPTable:
    def __init__(self) -> None:
        self.ARP_table = list()
        self.interface = None

    def get_ARP_table(self, interface:str, ips:str) -> int:
        # interface: 네트워크 인터페이스의 이름 ex) en0, wl0, 이더넷 등
        # ips: 탐색할 ip의 범위 ex) 192.168.0.1/24는 192.168.0.0 ~ 192.168.0.255까지 256개 ip 범위를 탐색
        # interface와 ips는 ARP scanning 창으로부터 사용자의 입력값을 받아서 설정됨
        
        self.ARP_table = list()
        self.interface = interface
        
        # # todo: scapy의 all verbose를 show하도록 설정하고,
        # # todo: scapy의 srp를 사용해 ARP response를 get
        # ans = None

        # for snd, rcv in ans:
        #     # todo: arp response (ans)로부터 ip address와 mac address를 get
        #     ip_addr = None
        #     mac_addr = None
        #     self.ARP_table.append((ip_addr, mac_addr))
        arp_request = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ips)
        ans, _ = srp(arp_request, iface=interface, timeout=2, verbose=True)
    
        for snd, rcv in ans:
            ip_addr = rcv.psrc
            mac_addr = rcv.hwsrc
            self.ARP_table.append((ip_addr, mac_addr))

    def default_ip_nif(self):
        # gateway의 IP address와 네트워크 어댑터(네트워크 인터페이스)의 이름을 가져온다.
        default = netifaces.gateways()['default']
        gateway_ip, nif = default[list(default.keys())[0]]
        if nif[0] == '{':
            # windows
            ip_info = netifaces.ifaddresses(nif)
            ip_addr = ip_info[netifaces.AF_INET][0]['addr']
            ps_if_addrs = psutil.net_if_addrs()
            exit_point = False
            for key in ps_if_addrs:
                for adress_family in ps_if_addrs[key]:
                    if adress_family.family == netifaces.AF_INET:
                        if adress_family.address == ip_addr:
                            nif = key
                            exit_point = True
                            break
                    if exit_point:
                        break

        return gateway_ip, nif
        
