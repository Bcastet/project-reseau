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
def load_model_characters_from_str(string_characters):
    characters = (string_characters.decode()).split("?")
    for i in range(len(characters)-1):
        
        this_char = characters[i].split("!")
        position_str = this_char[5].replace("(","")
        position_str = position_str.replace(")","")
        position_splitted = position_str.split(", ")
        pos = (int(position_splitted[0]),int(position_splitted[1]))
        model.add_character(this_char[4],True,int(this_char[0]),pos)

        model.characters[i].health = int(this_char[1])
        model.characters[i].immunity = int(this_char[2])
        model.characters[i].disarmed = int(this_char[3])


        model.characters[i].direction = int(this_char[6])


def load_model_from_server():
    s.send("LOAD_MODEL CHARACTERS".encode())
    load_model_characters_from_str((s.recv(4096)))




# initialization
pygame.display.init()
pygame.font.init()
clock = pygame.time.Clock()
s.send("GET_MAP_NAME".encode())
model = Model()
model.load_map(s.recv(4096).decode())
s.send(("NAME "+nickname).encode())
load_model_from_server()
view = GraphicView(model, nickname)
client = NetworkClientController(model, host, port, nickname)
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
