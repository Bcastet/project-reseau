#!/usr/bin/env python3
# -*- coding: Utf-8 -*
# Author: aurelien.esnard@u-bordeaux.fr

from model import *
from view import *
from keyboard import *
from network import *
import socket
import sys
import pygame

### python version ###
print("python version: {}.{}.{}".format(sys.version_info[0], sys.version_info[1], sys.version_info[2]))
print("pygame version: ", pygame.version.ver)

################################################################################
#                                 MAIN                                         #
################################################################################

# parse arguments
if len(sys.argv) != 4:
    print("Usage: {} host port nickname".format(sys.argv[0]))
    sys.exit()
host = sys.argv[1]
port = int(sys.argv[2])
nickname = sys.argv[3]

#connecting
addrs = socket.getaddrinfo(host,"http",0,socket.SOCK_STREAM)
ADDR=(host,port)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(ADDR)

#declarations





# initialization
pygame.display.init()
pygame.font.init()
clock = pygame.time.Clock()
s.send("GET_MAP_NAME".encode())
model = Model()
model.load_map(s.recv(4096).decode())
s.send(("NAME "+nickname).encode())
view = GraphicView(model, nickname)
client = NetworkClientController(model, host, port, nickname,s)
client.model.player=nickname
client.load_model_from_server(s)
kb = KeyboardController(client)

# main loop
while True:
    # make sure game doesn't run at more than FPS frames per second
    dt = clock.tick(FPS)
    if not kb.tick(dt): break
    if not client.tick(dt): break
    model.tick(dt)
    view.tick(dt)



# quit
print("Game Over!")
pygame.quit()
