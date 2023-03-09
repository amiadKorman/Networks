# Ex 7 - SYN Flood attack detector
# Author: Amiad Korman
from scapy.layers.inet import TCP, IP
from scapy.utils import rdpcap

HOME_IP = '100.64'


def threat_modeling(ip_src):
    """
    For every ip source, check if it might be a threat by checking if the src sends 10 or more syn requests and no
     syn-ack or ack at all, and of course that it not from the ip that we want to protect
    :param ip_src: dictionary of all ip sources and counter of syn, stn-ack and ack counters
    :return: list of all suspicious ip addresses
    """
    sus_ips = []
    for ip, value in ip_src.items():
        syn, syn_ack, ack = value
        if ack == 0 and syn_ack == 0 and syn >= 10 and not str(ip).startswith(HOME_IP):
            sus_ips.append(ip)

    return sus_ips


def main():
    ip_src = {}  # key: ip , value: [syn, syn-ack, ack]
    packets = rdpcap("SYNflood.pcapng")

    for pkt in packets:
        if pkt.haslayer(TCP):
            src = pkt[IP].src
            flag = pkt[TCP].flags
            if src not in ip_src:
                ip_src[src] = [0, 0, 0]

        if flag == 'S':  # SYN packet
            ip_src[src][0] += 1
        if flag == 'SA':  # SYN-ACK packet
            ip_src[src][1] += 1
        if flag == 'A':  # ACK packet
            ip_src[src][2] += 1

    print("finish reading packets, start analysing")
    sus_addresses = threat_modeling(ip_src)
    # export the suspicious addresses to a text file
    with open('suspicious_addresses.txt', 'w') as file:
        for address in sus_addresses:
            file.write(address + '\n')


if __name__ == '__main__':
    main()
