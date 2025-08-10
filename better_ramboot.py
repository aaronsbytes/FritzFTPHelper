#!/usr/bin/env python3

import argparse
import socket
from ftplib import FTP
from os import stat
import time
import os
import subprocess

def is_ip_reachable(ip, timeout=1):
    """Check if the IP address is reachable using the ping command."""
    try:
        # Use the ping command to check reachability
        output = subprocess.run(
            ["ping", "-c", "1", "-W", str(timeout), ip],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return output.returncode == 0
    except Exception as e:
        return False

def adam(cmd):
    print("> %s" % (cmd))
    resp = ftp.sendcmd(cmd)
    print("< %s" % (resp))
    assert resp[0:3] == "200"

parser = argparse.ArgumentParser(description='Tool to boot AVM EVA ramdisk images.')
parser.add_argument('ip', type=str, help='IP-address to transfer the image to')
parser.add_argument('image', type=str, help='Location of the ramdisk image')
parser.add_argument('--offset', type=lambda x: int(x, 0), help='Offset to load the image to in hex format with leading 0x. Only needed for non-lantiq devices.')
args = parser.parse_args()

size = stat(args.image).st_size
# arbitrary size limit, to prevent the address calculations from overflows etc.
assert size < 0x2000000

if args.offset:
    addr = size
    haddr = args.offset
else:
    # We need to align the address.
    # A page boundary seems to be sufficient on 7362sl and 7412
    addr = ((0x8000000 - size) & ~0xfff)
    haddr = 0x80000000 + addr


# Wait until device is reachable
ping_success = False
ping_attempts = 0
while not ping_success:
    if is_ip_reachable(args.ip):
        print(f"({args.ip}) Device found!                                                   ")
        ping_success = True
        break
    else:
        os.system("clear")
        print(f"({ping_attempts}) Waiting for {args.ip} ..                                             ", end="\r")
        ping_attempts += 1

# Try access FTP until successful
ftp_success = False
ftp_attempts = 0
while not ftp_success:
    img = open(args.image, "rb")
    print(f"({ftp_attempts}) Waiting for FTP server..                                                    ", end="\r")
    try:
        ftp = FTP(args.ip, 'adam2', 'adam2')
        print("SUCCESSFULLY ACCESSED FTP SERVER!")
        ftp_success = True
    except:
        ftp_attempts +=1
        continue
    time.sleep(.2)

ftp.set_pasv(True)
# The following parameters allow booting the avm recovery system with this script.
adam('SETENV memsize 0x%08x' % (addr))
adam('SETENV kernel_args_tmp mtdram1=0x%08x,0x88000000' % (haddr))
adam('MEDIA SDRAM')
ftp.storbinary('STOR 0x%08x 0x88000000' % (haddr), img)
img.close()
ftp.close()
