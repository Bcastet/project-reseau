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

view = GraphicView(model, "server")
#declarations


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
            msg1 , addr = i.recvfrom(2048)
            #print(msg)
            msg1=msg1.split("&".encode())
            for msg in msg1:
                if msg.startswith("NAME".encode()):
                    server.add_name(msg,i)
                if msg.startswith("GET_MAP_NAME".encode()):
                    i.send(map_file.encode())
                if msg.startswith("LOAD_MODEL".encode()):
                    msg_bis = msg.replace("LOAD_MODEL ".encode(),"".encode())

                    server.send_model(i,msg_bis)
                if msg.startswith("MOVE".encode()):
                    msg = msg.decode()
                    direction = msg.replace("MOVE ","")
                    server.model.move_character(server.nicks_list[i].decode(),int(direction))
                else:
                    if msg.startswith("DROP_BOMB".encode()):
                        server.model.drop_bomb(server.nicks_list[i].decode())



    #all elements computed, actualize clock and sending server_model
    dt = clock.tick(FPS)
    server.tick(dt)
    model.tick(dt)
    view.tick(dt)

# quit
print("Game Over!")
pygame.quit()
