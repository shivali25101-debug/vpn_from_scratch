import struct
import fcntl

TUNSETIFF = 0x400454ca
IFF_TUN = 0x0001
IFF_NO_PI = 0x1000

def create_tun():
    import subprocess
    print("Opening /dev/net/tun...")
    tun = open('/dev/net/tun', 'r+b', buffering=0)
    print("Attaching to tun0...")
    ifr = struct.pack('16sH', b'tun0', IFF_TUN | IFF_NO_PI)
    fcntl.ioctl(tun, TUNSETIFF, ifr)
    print("Bringing tun0 up...")
    r1 = subprocess.run(['ip', 'link', 'set', 'tun0', 'up'], capture_output=Tru>
    print(f"ip link result: {r1.returncode} {r1.stderr}")
    r2 = subprocess.run(['ip', 'addr', 'add', '10.8.0.1/24', 'dev', 'tun0'], ca>
    print(f"ip addr result: {r2.returncode} {r2.stderr}")
    return tun

def parse_packet(packet):
    version = packet[0] >> 4
    if version != 4:
        return None, None, None
    src = '.'.join(map(str, packet[12:16]))
    dst = '.'.join(map(str, packet[16:20]))
    proto = packet[9]
    if proto == 1:
        proto_name = "ICMP"
    elif proto == 6:
        proto_name = "TCP"
    elif proto == 17:
        proto_name = "UDP"
    else:
        proto_name = str(proto)
    return src, dst, proto_name

tun = create_tun()
print("Listening on tun0...")

while True:
    try:
        packet = tun.read(2048)
        version = packet[0] >> 4
        if version != 4:
            continue
        src = '.'.join(map(str, packet[12:16]))
        dst = '.'.join(map(str, packet[16:20]))
        proto = packet[9]
        if proto == 1:
            proto_name = "ICMP"
        elif proto == 6:
            proto_name = "TCP"
        elif proto == 17:
            proto_name = "UDP"
        else:
            proto_name = str(proto)
        print(f"src: {src} -> dst: {dst} | protocol: {proto_name} | {len(packet>
    except Exception as e:
        print(f"Error: {e}")
        continue
