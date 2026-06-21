import struct
import fcntl
import socket
import os
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305

TUNSETIFF = 0x400454ca
IFF_TUN = 0x0001
IFF_NO_PI = 0x1000

VM2_IP = '10.0.0.2'
VM2_PORT = 5000

def create_tun():
    tun = open('/dev/net/tun', 'r+b', buffering=0)
    ifr = struct.pack('16sH', b'tun0', IFF_TUN | IFF_NO_PI)
    fcntl.ioctl(tun, TUNSETIFF, ifr)
    os.system('ip link set tun0 up')
    os.system('ip addr add 10.8.0.1/24 dev tun0')
    os.system('sysctl -w net.ipv6.conf.tun0.disable_ipv6=1')
    return tun

private_key = X25519PrivateKey.generate()
public_key = private_key.public_key()
public_bytes = public_key.public_bytes(Encoding.Raw, PublicFormat.Raw)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

print("Sending public key to vm2...")
sock.sendto(public_bytes, (VM2_IP, VM2_PORT))

print("Waiting for vm2 public key...")
data, _ = sock.recvfrom(4096)

peer_public_key = X25519PublicKey.from_public_bytes(data)
shared_key = private_key.exchange(peer_public_key)
chacha = ChaCha20Poly1305(shared_key)
print("Shared key established! Tunnel is encrypted.")

tun = create_tun()
print(f"VPN sender running — forwarding encrypted packets to {VM2_IP}:{VM2_PORT}")

while True:
    try:
        packet = tun.read(2048)
        version = packet[0] >> 4
        if version != 4:
            continue
        nonce = os.urandom(12)
        encrypted = chacha.encrypt(nonce, packet, None)
        sock.sendto(nonce + encrypted, (VM2_IP, VM2_PORT))
        src = '.'.join(map(str, packet[12:16]))
        dst = '.'.join(map(str, packet[16:20]))
        print(f"Sent encrypted: {src} -> {dst} | {len(packet)} bytes")
    except Exception as e:
        print(f"Error: {e}")
        continue
