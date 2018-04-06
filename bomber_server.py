#!/usr/bin/env python3
# -*- coding: Utf-8 -*
# Author: aurelien.esnard@u-bordeaux.fr

from model import *
from view import *
from network import *
import socket
import select
import sys
import pygame

### python version ###
print("python version: {}.{}.{}".format(sys.version_info[0], sys.version_info[1], sys.version_info[2]))
print("pygame version: ", pygame.version.ver)

PORT=7777

sock = socket.socket(socket.AF_INET6,socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
sock.bind(('',PORT))
sock.listen(1)


################################################################################
#                                 MAIN                                         #
################################################################################

# parse arguments
if len(sys.argv) == 2:
    port = int(sys.argv[1])
    map_file = DEFAULT_MAP
elif len(sys.argv) == 3:
    port = int(sys.argv[1])
    map_file = sys.argv[2]
else:
    print("Usage: {} port [map_file]".format(sys.argv[0]))
    sys.exit()

# initialization
pygame.display.init()
pygame.font.init()
clock = pygame.time.Clock()
model = Model()
model.load_map(map_file)
for _ in range(10): model.add_fruit()
server = NetworkServerController(model, port)

# view = GraphicView(model, "server")
#declarations
def add_name(msg,socket):
    name = msg.replace("NAME ".encode(),"".encode())
    name_bis = name.replace("\n".encode(),"".encode())
    model.add_character(name_bis.decode(),True)
    server.nicks_list[socket]=name_bis

def send_model_characters(socket):
    char = ""
    for i in range(len(model.characters)):
        char = char+((str(model.characters[i].kind)+"!"+str(model.characters[i].health)+"!"+str(model.characters[i].immunity)+"!"+str(model.characters[i].disarmed)
        +"!"+str(model.characters[i].nickname)+"!"+str(model.characters[i].pos)+"!"+str(model.characters[i].direction)+"?"))
    socket.send(char.encode())
    print(char+"\n")

def send_model_bombs(socket):
    bombs = ""
    for i in range(len(model.bombs)):
        bombs = bombs+((str(model.bomb[i].pos)+"!"+str(model.bomb[i].max_range)+"!"+str(model.bomb[i].countdown)+"!"+str(model.bomb[i].time_to_explode)+"?"))
    socket.send(bombs.encode())
    print(bombs+"\n")

def send_model_players(socket):
    socket.send(str(model.player).encode())

def send_model_fruits(socket):


def send_model(socket_client,msg):
    if msg.startswith("CHARACTERS".encode()):
        send_model_characters(socket_client)
    if msg.startswith("FRUITS".encode()) :
        send_model_fruits(socket_client)
    if msg.startswith("BOMBS".encode()):
        send_model_bombs(socket_client)
    if msg.startswith("PLAYERS".encode()):
        send_model_players(socket_client)


# main loop
while True:
    # make sure game doesn't run at more than FPS frames per second
    r, _, _ = select.select(server.get_socket_client_list()+[sock],[],[])
    new_element_this_tick= []
    for i in r:
        if i==sock:
            sock_received, addr = sock.accept()
            server.add_socket(sock_received)
            server.nicks_list[sock_received]="NO NAME"
        else:
            msg , addr = i.recvfrom(2048)
            if msg.startswith("NAME".encode()):
                add_name(msg,i)
            if msg.startswith("GET_MAP_NAME".encode()):
                i.send(map_file.encode())
            if msg.startswith("LOAD_MODEL".encode()):
                msg_bis = msg.replace("LOAD_MODEL ".encode(),"".encode())
                send_model(i,msg_bis)
                new_element_this_tick.append("CHARACTER")
            if msg.startswith("MOVE".encode()):
                msg_bis = msg.replace("MOVE ".encode(),"".encode())



    #all elements computed, actualize clock and sending server_model
    dt = clock.tick(FPS)
    server.tick(dt)
    model.tick(dt)
    # view.tick(dt)

# quit
print("Game Over!")
pygame.quit()
