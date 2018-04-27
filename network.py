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
        self.socket_client_list={}
        self.nicks_list={}

    def get_socket_client_list(self):
        return list(self.socket_client_list.keys())

    def add_socket(self,socket):
        self.socket_client_list[socket]=0

    # time event
    def kick(self,socket):
            self.model.kill_character(self.nicks_list[socket].decode())
            del(self.socket_client_list[socket])

    def tick(self, dt):
        to_kick=[]
        if random.randint(0,100)==1:
            self.model.add_fruit()
        for i in self.socket_client_list.keys():
            self.socket_client_list[i]=self.socket_client_list[i]+1
            if self.socket_client_list[i]==40:
                to_kick.append(i)
        for i in to_kick:
            self.kick(i)
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


    def send_model_bombs(self,socket):
        bombs = "!"
        for i in range(len(self.model.bombs)):
            bombs = bombs+((str(self.model.bombs[i].pos)+"!"+str(self.model.bombs[i].max_range)+"!"+str(self.model.bombs[i].countdown)+"!"+str(self.model.bombs[i].time_to_explode)+"?"))
        socket.send(bombs.encode())


    def send_model_fruits(self,socket):
        fruits = "!"
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

    def __init__(self, model, host, port, nickname,socket_server):
        self.model = model
        self.host = host
        self.port = port
        self.nickname = nickname
        self.socket_server = socket_server


    # keyboard events

    def keyboard_quit(self):
        print("=> event \"quit\"")
        return False

    def keyboard_move_character(self, direction):
        print("=> event \"keyboard move direction\" {}".format(DIRECTIONS_STR[direction]))
        self.model.move_character(self.nickname,direction)
        self.socket_server.send(("MOVE {}&".format(direction)).encode())
        return True

    def keyboard_drop_bomb(self):
        print("=> event \"keyboard drop bomb\"")
        self.model.drop_bomb(self.nickname)
        self.socket_server.send("DROP_BOMB&".encode())
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
            if self.model.look(this_char[4])==None:
                if this_char[4]==self.nickname:
                    self.model.add_character(this_char[4],True,int(this_char[0]),pos)
                else:
                    self.model.add_character(this_char[4],False,int(this_char[0]),pos)
            self.model.characters[i].pos = pos
            self.model.characters[i].health = int(this_char[1])
            self.model.characters[i].immunity = int(this_char[2])
            self.model.characters[i].disarmed = int(this_char[3])
            self.model.characters[i].direction = int(this_char[6])
            if this_char[4]==self.nickname:
                self.model.player.pos=pos
                self.model.player.health = int(this_char[1])
                self.model.player.immunity = int(this_char[2])
                self.model.player.disarmed = int(this_char[3])
                self.model.player.direction = int(this_char[6])

    def load_model_fruits_from_str(self,string_fruits):

        fruits = (string_fruits.decode().split("?"))
        for i in range(len(fruits)-1):
            this_fruit = fruits[i].split("!")
            if(len(this_fruit)>2):
                pos = self.position_from_str(this_fruit[1])
                self.model.add_fruit(int(this_fruit[2]),pos)
            else:
                pos = self.position_from_str(this_fruit[0])
                self.model.add_fruit(int(this_fruit[1]),pos)

    def load_model_fruits_from_str_no_add(self, string_fruits):
        fruits = (string_fruits.decode().split("?"))
        for i in range(len(fruits)-1):
            this_fruit = fruits[i].split("!")
            if(len(this_fruit)>2):
                pos = self.position_from_str(this_fruit[1])
                self.model.fruits[i].kind=int(this_fruit[2])
                self.model.fruits[i].pos=pos
            else:
                pos = self.position_from_str(this_fruit[0])
                if i>=len(self.model.fruits):
                    self.model.add_fruit(int(this_fruit[1]),pos)
                else:
                    self.model.fruits[i].kind=int(this_fruit[1])
                    self.model.fruits[i].pos=pos

    def load_model_bombs_from_str(self,string_bombs):
        bombs = (string_bombs.decode().split("?"))
        for i in range(len(bombs)-1):
            this_bomb = bombs[i].split("!")
            if i==len(self.model.bombs):
                print(this_bomb)
                if(len(this_bomb)<=4):
                    print(this_bomb[0])
                    pos = self.position_from_str(this_bomb[0])
                else:
                    print(this_bomb[1])
                    pos = self.position_from_str(this_bomb[1])
                boum=Bomb(self.model.map,pos)
                self.model.bombs.append(boum)
            if(len(this_bomb)<=4):
                pos = self.position_from_str(this_bomb[0])
                self.model.bombs[i].pos=pos
                self.model.bombs[i].max_range = this_bomb[1]
                self.model.bombs[i].countdown = int(this_bomb[2])
                self.model.bombs[i].time_to_explode = int(this_bomb[3])
            else:
                pos = self.position_from_str(this_bomb[1])
                self.model.bombs[i].pos=pos
                self.model.bombs[i].max_range = this_bomb[2]
                self.model.bombs[i].countdown = int(this_bomb[3])
                self.model.bombs[i].time_to_explode = int(this_bomb[4])

    def load_model_from_server(self,socket):
        socket.send("LOAD_MODEL CHARACTERS&".encode())
        self.load_model_characters_from_str((socket.recv(4096)))
        socket.send("LOAD_MODEL FRUITS&".encode())
        self.load_model_fruits_from_str((socket.recv(4096)))


    def get_model(self):
        self.socket_server.send("LOAD_MODEL CHARACTERS&".encode())
        self.load_model_characters_from_str(self.socket_server.recv(4096))
        self.socket_server.send("LOAD_MODEL FRUITS&".encode())
        self.load_model_fruits_from_str_no_add(self.socket_server.recv(4096))
        self.socket_server.send("LOAD_MODEL BOMBS&".encode())
        msg = self.socket_server.recv(4096)
        self.load_model_bombs_from_str(msg)
    # time event

    def tick(self, dt):
        self.get_model()
        self.model.tick(dt)
        return True
