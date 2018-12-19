# -*- coding: utf-8 -*-
"""
Created on Tue Nov 27 12:32:27 2018

@author: Utilisateur
"""
#envoi de byte recept de byte et hash de byte
import socket as so
import datetime as dt
import hashlib as hl
import _thread as td
import socketserver as ss
import configparser as cp
import pickle
import select
class Server:

    def __init__(self):
        self.file = File('server.ini')
        self.ip_address = self.file.getKey('node','ip_address')
        self.port = 5001
        self.serverSocket = so.socket(so.AF_INET,so.SOCK_STREAM)
        self.serverSocket.setsockopt(so.SOL_SOCKET,so.SO_REUSEADDR,1)
        self.serverSocket.bind((self.ip_address,self.port))
        self.serverSocket.listen(10)
        self.list_client = []
        self.list_connect = {}
        self.ad = []


        self.identifier = {'alice':'ecila','jb':'bj','sam':'mas', 'kayak':'kayak', 'bob':'bob'}
        #on met les identifiant ici???

    def connect(self): #launch TCP server
        #tcp_serv = ss.TCPServer((self.ip_address,self.port),TCPHandler)
        while 1:
            self.connectionSocket, self.addr = self.serverSocket.accept()
            td.start_new_thread(self.handle_message_client,())

    def handle_message_client(self):
        while 1:
            conn = self.connectionSocket
            try:
                conn.sendall('entre user and psw'.encode('utf-8'))
            except ConnectionResetError:
                pass
            try:
                use_psw = conn.recv(1024)
            except:
                pass
            #pwc = use_psw.decode('utf-8')
            #print(len(str(use_psw.decode('utf-8'))))
            user_id = use_psw.split()#list of string
            #print(user_id[1].decode('utf-8'),user_id[0].decode('utf-8'))
            #psw = use_psw.split() #string
            self.ad.append(self.addr[0])
            #print(use_psw.decode())
            if self.user_is_present(user_id[0].decode('utf-8'),user_id[1].decode('utf-8'),conn)==True:
                nonce  = str(dt.datetime.now().year) + str(dt.datetime.now().month) + str(dt.datetime.now().day) + str(dt.datetime.now().hour)+str(dt.datetime.now().minute)+str(dt.datetime.now().second)
                conn.sendall(nonce.encode('utf-8'))
                hash_nonce = hl.sha256((nonce +user_id[1].decode('utf-8')).encode('utf-8')).hexdigest() #string
                hashed_nonce = conn.recv(1024)
                if hash_nonce ==hashed_nonce.decode('utf-8'): #0 success 1 error
                    conn.sendall('0'.encode('utf-8'))
                    self.file.addKey('neighbour',self.addr[0])
                    #clients = pickle.dumps(self.file.getListSection('neighbour'))
                    #self.list_connect.append(self.connectionSocket)
                    self.list_connect[self.addr[0]] = self.connectionSocket
                    tail = len(self.list_connect.keys())
                    
                    if tail!=1 and tail !=0: #at least 2 clients
                        for ipd, sock in self.list_connect.items():
                            if sock is not self.connectionSocket: # send newly arrived IP to everyone
                                sock.sendall(self.addr[0].encode())
                            else: #send IP already there
                                for ip in self.list_connect.keys():
                                    if ip is not self.addr[0]:
                                        print('ip',ip)
                                        print(ip,sock)
                                        sock.sendall((ip+' ').encode())
                                
                    try:
                        getout = conn.recv(1024).decode('utf-8')
                        out_message = getout.split()
                    except so.error as e:
                        print(out_message[1] +'NEXT TIME TYPE OUT BEFORE EXITING')
                    if out_message[0] == 'out':
                        del self.list_connect[out_message[1]]
                        out_clients = ('out '+out_message[1]).encode()
                        for ipd, sock in self.list_connect.items():
                            sock.sendall(out_clients)
                        print('bye '+out_message[1])
                        conn.close()
                        break

                else: #failed to hash
                    conn.sendall('1'.encode('utf-8'))
                    break;

            else: #user is not present
                break;

    def user_is_present(self,user,psw,conn):
        is_present = False
        if user in self.identifier:
            if self.identifier[user] == psw:
                is_present = True
                conn.sendall('good userid, verifie the nonce'.encode('utf-8'))
            else:
                conn.sendall('wrong psw'.encode('utf-8'))
        else:
            conn.sendall('wrong user name'.encode())
        return is_present



class File:
    def __init__(self, filename): #addsection before add key
        self.filename = filename
        self.config = cp.ConfigParser(allow_no_value=True)
        self.file = open(self.filename,'r+')
        self.file.close()

    def addSection(self,section): 
        self.config.add_section(section)
        with open(self.filename,'a') as f:
            self.config.write(f)

    def getKey(self, section, key):
        self.config.read(self.filename)
        return self.config.get(section,key)
    def getListSection(self,section):
        self.config.read(self.filename)
        try:
            l = list(self.config[section].keys())
            return l
        except KeyError:
            print('LIST '+neighbour+' IS EMPTY')
            return []
        


    def addKey(self, section, key, value =None):
        try:
            self.config.set(section,key,value)
            with open(self.filename,'r+') as f:
                self.config.write(f)
        except KeyError:
            print('file.addKey')
    def deleteKey(self,section,key):
        with open(self.filename,'r+') as f:
            self.config.readfp(f)
            self.config.remove_option(section,key)
            f.seek(0)
            self.config.write(f)
            f.truncate()

    def deleteSec(self,section):
        with open(self.filename,'r+') as f:
            self.config.readfp(f)
            self.config.remove_section(section)
            f.seek(0)
            self.config.write(f)
            f.truncate()
    def section(self):
        self.config.read(self.filename)
        ls = self.config.sections()
        return ls


if __name__ == '__main__' :
    print('SERVER HAVE BEEN LAUNCH')
    s = Server()
    s.connect()
