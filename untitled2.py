#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 12 16:21:08 2023

@author: acomeau
"""

import socket
import os
import subprocess
import time

def skyXsndPkt2(command_packet: str):
    address_tuple = ('127.0.0.1', 3040)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as the_socket:
        the_socket.connect(address_tuple)
        bytes_to_send = bytes(command_packet, 'utf-8')
        the_socket.sendall(bytes_to_send)
        returned_bytes = the_socket.recv(1024)
        result = returned_bytes.decode('utf=8')
        print(result)
    return result

subProc = subprocess.Popen('/home/acomeau/TheSkyX13507/TheSkyX', stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)

time.sleep(10)

cmd = "/* Java Script *//* Socket Start Packet */ccdsoftCamera.Connect();/* Socket End Packet */"
skyXsndPkt2(cmd)

for ndx in range(100):
    if os.path.exists('/home/acomeau/Library/Telescopium/20230510/Light -10C M101PointingExp OSC 10s 2bin #001 20230511-013840.SRC'):
        os.remove('/home/acomeau/Library/Telescopium/20230510/Light -10C M101PointingExp OSC 10s 2bin #001 20230511-013840.SRC')
    cmd = "/* Java Script *//* Socket Start Packet */ImageLink.pathToFITS = '/home/acomeau/Library/Telescopium/20230510/Light -10C M101PointingExp OSC 10s 2bin #001 20230511-013840.fit';ImageLink.scale = 0.78;ImageLink.unknownScale = 1;ImageLink.execute();Out = ImageLinkResults.errorCode;Out += '|' + ImageLinkResults.succeeded;Out += '|' + ImageLinkResults.searchAborted;Out += '|' + ImageLinkResults.errorText;Out += '|' + ImageLinkResults.imageScale;Out += '|' + ImageLinkResults.imagePositionAngle;Out += '|' + ImageLinkResults.imageCenterRAJ2000;Out += '|' + ImageLinkResults.imageCenterDecJ2000;Out += '|' + ImageLinkResults.imageFWHMInArcSeconds;/* Socket End Packet */"
    skyXsndPkt2(cmd)
    
