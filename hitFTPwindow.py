#!/usr/bin/env python3
import argparse
from ftplib import FTP
import os
import subprocess

class FritzBoxFTPHelper:
    def __init__(self):
        parser = argparse.ArgumentParser(description='Helper script to get a FTP shell to your Fritz!Box.')
        parser.add_argument('ip', type=str, help='IP-address to transfer the image to')
        self.args = parser.parse_args()

        # Wait for the Fritz!Box to be reachable
        self.wait_for_device()

        # Wait for the ftp connection
        self.ftp = self.wait_for_ftp()

        if self.ftp == FTP():
            print("Couldn't access FTP!")
            exit(0)

        print(self.ftp.getwelcome())

        while True:
            cmd = input("adam2@fritz.box ~# ")

            if cmd.lower() == "bye":
                self.ftp.close()

            resp = self.adam(cmd)
            print(resp)

    def ip_is_reachable(self, ip, timeout=1):
        output = None
        try:
            # Use the ping command to check reachability
            output = subprocess.run(
                ["ping", "-c", "1", "-W", str(timeout), ip],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        except Exception as e:
            print(e)
        return output.returncode == 0

    def adam(self, cmd):
        try:
            resp = self.ftp.voidcmd(cmd)
            return resp
        except Exception as e:
            return f"{e}"

    def wait_for_device(self):
        # Wait until device is reachable
        ping_success = False
        ping_attempts = 0
        while not ping_success:
            if self.ip_is_reachable(self.args.ip):
                ping_success = True
            else:
                os.system("clear")
                ping_attempts += 1

    def wait_for_ftp(self):
        # Try access FTP until successful
        ftp_success = False
        ftp_attempts = 0
        ftp = FTP()
        while not ftp_success:
            try:
                ftp = FTP(self.args.ip, 'adam2', 'adam2')
                ftp_success = True
            except:
                ftp_attempts += 1
                continue

        return ftp


FritzBoxFTPHelper = FritzBoxFTPHelper()
