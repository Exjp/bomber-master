# -*- coding: Utf-8 -*
# Author: aurelien.esnard@u-bordeaux.fr

import socket
import select
import pygame
from model import *

################################################################################
#                          NETWORK SERVER CONTROLLER                           #
################################################################################

class NetworkServerController:

    def __init__(self, model, port):
        self.model = model
        self.port = port
        self.socket = self.socket_creation('',port)
        self.sockets_list = [self.socket]
        self.players_list = [] #liste de (nickname,socket)
        # ...

    # time event

    def tick(self, dt):

        conn_list, wlist, xlist = select.select(self.sockets_list,[],[], 1/60)
        message_str = self.model_to_string()
        for conn in conn_list:
            if (conn == self.socket):
                conn_client, adresse = conn.accept() #Accepte une connexion entrante (crée le socket 'conn_client')
                self.sockets_list.append(conn_client) #Ajoute le socket a la liste
                self.model.add_character("me", isplayer = True)
                map_string = self.map_to_string()
                map_string_en = map_string.encode()
                conn_client.send(map_string_en)

            else:
                message_recu = ""
                try:
                    message_recu = conn.recv(10000)
                except:
                    print("Client disconnected\n\n")
                if(len(message_recu) == 0): #Verification du message
                    name_player_tokill = "INCORRECT"
                    for player in self.players_list: #Cherche le nom du joueur
                        if (player[1] == conn):
                            name_player_tokill = player[0]
                            character_tokill = self.model.look(name_player_tokill)
                            if character_tokill:
                                self.model.kill_character(name_player_tokill)
                            self.players_list.remove(player) #Enlève de la liste des joueurs
                            self.sockets_list.remove (conn)  #Enlève de la liste des sockets
                            break
                    if (name_player_tokill == "INCORRECT"):
                        print ("Error : leaving name not found\n")
                    conn.close()
                    break
                message_recu_d = message_recu.decode()
                self.process_message(message_recu_d,conn)
        #Envoi du message
        for socket_m in self.sockets_list:
            if (socket_m == self.socket):
                pass
            else:
                message = message_str.encode()
                socket_m.send(message)
        return True

    def socket_creation(self,ip,port):
        TCP_IP = ip
        TCP_PORT = self.port

        s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((TCP_IP, TCP_PORT))
        s.listen(1)
        return s

    def socket_to_nick(self,socket_c):
        nickname_player = "INCORRECT"
        for player in self.players_list:
            if (player[1] == socket_c):
                nickname_player = player[0]
                break
        return nickname_player


    def process_message(self,str_c,expediteur):

        list_m = str_c.split(" ")
        #print(str_c)
        if (list_m[0] == "NICK"):
            nickname = list_m[1]
            counter = 0
            alreadytaken = 1
            while (alreadytaken==1):
                alreadytaken = 0
                for nick_l in self.players_list:
                    if nick_l[0] == nickname:
                        nickname += "*"
                        alreadytaken = 1
                        break

            self.model.characters[-1].nickname = nickname
            print("Player name : " + nickname)
            self.players_list.append((nickname,expediteur))
            #print(self.players_list)
            return
        nickname_exp = self.socket_to_nick(expediteur)
        character_exp = self.model.look(nickname_exp)
        if not character_exp:
            return
        if (list_m[0] == "MOVE"):
            direction_m = int(list_m[1])
            nickname_tomove = self.socket_to_nick(expediteur)
            self.model.move_character(nickname_tomove,direction_m)
            return
        if (list_m[0] == "BOMB"):
            nickname_bomber = self.socket_to_nick(expediteur)
            self.model.drop_bomb(nickname_bomber)

        return

    def map_to_string(self):
        str_m = "MAP ARRAY"
        #print(self.model.map.array)
        for row in self.model.map.array:
            str_m += " ROW " + " ".join(row)
        str_m += " WIDTH " + str(self.model.map.width) + " HEIGHT " + str(self.model.map.height)
        str_m += " END \n"
        #print(str_m)
        return str_m

    def model_to_string(self):
        str_m = "MODEL "
        str_m += "CHARACTERS"
        for chara in self.model.characters:
            str_m += " KIND " + str(chara.kind)
            str_m += " HEALTH " + str(chara.health)
            str_m += " IMMUNITY " + str(chara.immunity)
            str_m += " DISARMED " + str(chara.disarmed)
            str_m += " NICKNAME " + chara.nickname
            str_m += " POS " + str(chara.pos[0]) + " " + str(chara.pos[1])
            str_m += " DIRECTION " + str(chara.direction)
        str_m += " FRUITS"
        for fruit in self.model.fruits:
            str_m += " KIND " + str(fruit.kind)
            str_m += " POS " + str(fruit.pos[0]) + " " + str(fruit.pos[1])
        str_m += " BOMBS"
        for bomb in self.model.bombs:
            str_m += " POS " + str(bomb.pos[0]) + " " + str(bomb.pos[1])
            str_m += " MAX_RANGE " + str(bomb.max_range)
            str_m += " COUNTDOWN " + str(bomb.countdown)
            str_m += " TIME_TO_EXPLODE " + str(bomb.time_to_explode)
        str_m += " END \n"
        return str_m





################################################################################
#                          NETWORK CLIENT CONTROLLER                           #
################################################################################

class NetworkClientController:

    def __init__(self, model, host, port, nickname):
        self.model = model
        self.host = host
        self.port = port
        self.nickname = nickname
        self.socket = self.socket_creation(host,port)

    def socket_creation(self,ip,port):
        TCP_IP = ip
        TCP_PORT = port

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))
        nickname_message = "NICK " + self.nickname
        nickname_encod = nickname_message.encode()
        s.send(nickname_encod)
        return s


    # keyboard events

    def keyboard_quit(self):
        print("=> event \"quit\"")
        return False

    def keyboard_move_character(self, direction):
        print("=> event \"keyboard move direction\" {}".format(DIRECTIONS_STR[direction]))
        move_string = "MOVE " + str(direction) + " "
        move_string_c = move_string.encode()
        self.socket.send(move_string_c)
        return True

    def keyboard_drop_bomb(self):
        print("=> event \"keyboard drop bomb\"")
        self.socket.send("BOMB ".encode())
        return True

    # time event

    def tick(self, dt):
        MESSAGE = ""
        bytearray = MESSAGE.encode()
        self.socket.send(bytearray)
        BUFFER_SIZE = 10000
        data = self.socket.recv(BUFFER_SIZE)
        string = data.decode()
        self.string_to_model(string)

        #self.socket.close()
        #print ("received data:", string)
        return True

    def string_to_model(self,str_m):
        #print(str_m)
        list_m = str_m.split(" ")
        i = 0
        if (list_m[i] == "MAP"):
            i+=1
            if (list_m[i] != "ARRAY"):
                return
            i+=1
            row_m = -1
            self.model.map.array=[]
            while (list_m[i] != "WIDTH"):
                if(list_m[i] == "ROW"):
                    row_m +=1
                    self.model.map.array.append([])
                elif(list_m[i] in ['w','x','z','0','1','2']):
                    self.model.map.array[row_m].append(list_m[i])
                i+=1
            i+=1
            self.model.map.width = int(list_m[i])
            i+=1
            if (list_m[i] != "HEIGHT"):
                return
            i+=1
            self.model.map.height = int(list_m[i])

            print("MAP LOADED OK\n")
            return
        if (list_m[i] != "MODEL"):
            return
        i+=1
        if (list_m[i] != "CHARACTERS"):
            return
        i+=1
        self.model.characters = []
        while (list_m[i] != "FRUITS"):
            if(list_m[i] == "KIND"):
                i+=1
                while(list_m[i] != "KIND" and list_m[i] != "FRUITS"):
                    char_kind = int(list_m[i])
                    i+=1
                    if (list_m[i] == "HEALTH"):
                        i+=1
                        char_health = int(list_m[i])
                        i+=1
                    if (list_m[i] == "IMMUNITY"):
                        i+=1
                        char_immu = int(list_m[i])
                        i+=1
                    if (list_m[i] == "DISARMED"):
                        i+=1
                        char_dis = int(list_m[i])
                        i+=1
                    if (list_m[i] == "NICKNAME"):
                        i+=1
                        char_nick = list_m[i]
                        i+=1
                    if (list_m[i] == "POS"):
                        i+=1
                        char_pos = (int(list_m[i]), int(list_m[i+1]))
                        i+=2
                    if (list_m[i] == "DIRECTION"):
                        i+=1
                        char_direction = int(list_m[i])
                        i+=1
                    character_m = Character(char_nick, char_kind, self.model.map, char_pos)
                    character_m.health = char_health
                    character_m.immunity = char_immu
                    character_m.disarmed = char_dis
                    character_m.direction = char_direction
                    self.model.characters.append(character_m)
        self.model.fruits = []
        i+=1
        while (list_m[i] != "BOMBS"):

            if(list_m[i] == "KIND"):
                i+=1
                fruit_kind = int(list_m[i])
                i+=1
                if(list_m[i] == "POS"):
                    i+=1
                    fruit_pos = (int(list_m[i]), int(list_m[i+1]))
                    i+=2
                self.model.fruits.append(Fruit(fruit_kind, self.model.map, fruit_pos))
        self.model.bombs = []
        i+=1
        while (list_m[i] != "END"):
            if(list_m[i] == "POS"):
                i+=1
                bomb_pos = (int(list_m[i]), int(list_m[i+1]))
                i+=2
                if(list_m[i] == "MAX_RANGE"):
                    i+=1
                    bomb_maxr = int(list_m[i])
                    i+=1
                if(list_m[i] == "COUNTDOWN"):
                    i+=1
                    bomb_count = int(list_m[i])
                    i+=1
                if(list_m[i] == "TIME_TO_EXPLODE"):
                    i+=1
                    bomb_time = int(list_m[i])
                    i+=1
                bomb_m = Bomb(self.model.map, bomb_pos)
                bomb_m.max_range = bomb_maxr
                bomb_m.countdown = bomb_count
                bomb_m.time_to_explode = bomb_time
                self.model.bombs.append(bomb_m)
                #print("Bombs : ")
                #print(bomb_pos)
