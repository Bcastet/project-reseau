# -*- coding: Utf-8 -*
# Author: aurelien.esnard@u-bordeaux.fr

from model import *

################################################################################
#                          NETWORK SERVER CONTROLLER                           #
################################################################################

class NetworkServerController:

    def __init__(self, model, port):
        self.model = model
        self.port = port
        self.socket_client_list=[]
        self.nicks_list={}
        self.new_element_this_tick=[]

    def get_socket_client_list(self):
        return self.socket_client_list

    def add_socket(self,socket):
        self.socket_client_list.append(socket)

    # time event

    def tick(self, dt):
        # ...
        return True
    def add_name(self,msg,socket):
        name = msg.replace("NAME ".encode(),"".encode())
        name_bis = name.replace("\n".encode(),"".encode())
        self.model.add_character(name_bis.decode(),True)
        self.nicks_list[socket]=name_bis

    def send_model_characters(self,socket):
        char = ""
        for i in range(len(self.model.characters)):
            char = char+((str(self.model.characters[i].kind)+"!"+str(self.model.characters[i].health)+"!"+str(self.model.characters[i].immunity)+"!"+str(self.model.characters[i].disarmed)
            +"!"+str(self.model.characters[i].nickname)+"!"+str(self.model.characters[i].pos)+"!"+str(self.model.characters[i].direction)+"?"))
        socket.send(char.encode())
        print(char+"\n")

    def send_model_bombs(self,socket):
        bombs = ""
        for i in range(len(self.model.bombs)):
            bombs = bombs+((str(self.model.bomb[i].pos)+"!"+str(self.model.bomb[i].max_range)+"!"+str(self.model.bomb[i].countdown)+"!"+str(self.model.bomb[i].time_to_explode)+"?"))
        socket.send(self.bombs.encode())
        print(bombs+"\n")

    def send_model_fruits(self,socket):
        fruits = ""
        for i in self.model.fruits:
            fruits = fruits + (str(i.pos)) + "!" + (str(i.kind)) + "?"
        socket.send(fruits.encode())

    def send_model(self,socket_client,msg):
        if msg.startswith("CHARACTERS".encode()):
            self.send_model_characters(socket_client)
        if msg.startswith("FRUITS".encode()) :
            self.send_model_fruits(socket_client)
        if msg.startswith("BOMBS".encode()):
            self.send_model_bombs(socket_client)
        if msg.startswith("PLAYERS".encode()):
            self.send_model_players(socket_client)


################################################################################
#                          NETWORK CLIENT CONTROLLER                           #
################################################################################

class NetworkClientController:

    def __init__(self, model, host, port, nickname):
        self.model = model
        self.host = host
        self.port = port
        self.nickname = nickname
        # ...

    # keyboard events

    def keyboard_quit(self):
        print("=> event \"quit\"")
        return False

    def keyboard_move_character(self, direction):
        print("=> event \"keyboard move direction\" {}".format(DIRECTIONS_STR[direction]))
        # ...
        return True

    def keyboard_drop_bomb(self):
        print("=> event \"keyboard drop bomb\"")
        # ...
        return True

    def position_from_str(self,string):
        string = string.replace("(","")
        string = string.replace(")","")
        pos_splitted = string.split(", ")
        return (int(pos_splitted[0]),int(pos_splitted[1]))

    def load_model_characters_from_str(self,string_characters):
        characters = (string_characters.decode()).split("?")
        for i in range(len(characters)-1):
            this_char = characters[i].split("!")
            position_str = this_char[5].replace("(","")
            position_str = position_str.replace(")","")
            position_splitted = position_str.split(", ")
            pos = (int(position_splitted[0]),int(position_splitted[1]))
            self.model.add_character(this_char[4],True,int(this_char[0]),pos)
            self.model.characters[i].health = int(this_char[1])
            self.model.characters[i].immunity = int(this_char[2])
            self.model.characters[i].disarmed = int(this_char[3])
            self.model.characters[i].direction = int(this_char[6])

    def load_model_fruits_from_str(self,string_fruits):
        fruits = (string_fruits.decode()).split("?")
        for i in range(len(fruits)-1):
            this_fruit = fruits[i].split("!")
            position_str = this_fruit[0].replace("(","")
            position_str = position_str.replace(")","")
            position_splitted = position_str.split(", ")
            pos = (int(position_splitted[0]),int(position_splitted[1]))

            self.model.add_fruit(int(this_fruit[1]),pos)

    def load_model_players_from_str(self,string_players):
        players = (string_players.decode()).split("?")
        for i in range(len(players)-1):
            print(i)
            self.model.players.append(i)

    def load_model_from_server(self,socket):
        socket.send("LOAD_MODEL CHARACTERS".encode())
        self.load_model_characters_from_str((socket.recv(4096)))
        socket.send("LOAD_MODEL FRUITS".encode())
        self.load_model_fruits_from_str((socket.recv(4096)))
    # time event

    def tick(self, dt):
        # ...
        return True
