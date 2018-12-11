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
class Server1:
    
    def __init__(self):
        self.file = File('server.ini')
        #print(self.file.getKey('node','ip_address'))
        self.ip_address = self.file.getKey('node','ip_address')
        self.port = 5001
        self.serverSocket = so.socket(so.AF_INET,so.SOCK_STREAM)
        self.serverSocket.setsockopt(so.SOL_SOCKET,so.SO_REUSEADDR,1)
        self.serverSocket.bind((self.ip_address,self.port))
        self.serverSocket.listen(10)
        self.list_client = []
        self.list_connect = []
        self.ad = []
        self.list_connect.append(self.serverSocket) #problème car devient vide après
           
        
        self.identifier = {'alice':'ecila','jb':'bj'}
        #on met les identifiant ici???
        
    def launch_connection(self): #launch TCP server
        #tcp_serv = ss.TCPServer((self.ip_address,self.port),TCPHandler)
        while 1:
            self.connectionSocket, self.addr = self.serverSocket.accept()
            a = td.start_new_thread(self.handle_message_client,())
          
    def handle_message_client(self):
        while 1:
            conn = self.connectionSocket
            conn.sendall('entre user and psw'.encode('utf-8'))
            use_psw = conn.recv(1024)
            #pwc = use_psw.decode('utf-8')
            #print(len(str(use_psw.decode('utf-8'))))
            user_id = use_psw.split()#list of string
            #print(user_id[0].decode('utf-8'))
            #psw = use_psw.split() #string
            self.ad.append(self.addr[0])
            if self.user_is_present(user_id[0].decode('utf-8'),user_id[1].decode('utf-8'),conn)==True:
                nonce  = str(dt.datetime.now().year) + str(dt.datetime.now().month) + str(dt.datetime.now().day) + str(dt.datetime.now().hour)+str(dt.datetime.now().minute)+str(dt.datetime.now().second)
                conn.sendall(nonce.encode('utf-8'))
                
                hash_nonce = hl.sha256((nonce +user_id[1].decode('utf-8')).encode('utf-8')).hexdigest() #string
                hashed_nonce = conn.recv(1024)
                if hash_nonce ==hashed_nonce.decode('utf-8'): #0 success 1 error
                    conn.sendall('0'.encode('utf-8'))
                    self.file.addKey('neighbour',self.addr[0])
                    #clients = pickle.dumps(self.file.getListSection('neighbour'))
                    self.list_connect.append(conn)
                    while True: #STUCK HERE
                        #read_socs, write_socs, err_socs = select.select(self.list_connect,[],[])
                        #out_message = conn.recv(1024).decode('utf-8')
                        for i in range(1,len(self.list_connect)):
                            if (self.list_connect[i] is not conn):# or (sock is not self.serverSocket):
                                self.list_connect[i].sendall(self.addr[0].encode('utf-8'))
                            else:
                                out_message = self.list_connect[i].recv(1024).decode('utf-8')
                                if out_message:
                                    if out_message == 'out':
                                        print(self.list_connect)
                                        self.list_connect[i].close()
                                        self.list_connect.remove(self.list_connect[i])
                                        print(self.list_connect)
                                        break
                                    else:
                                        pass #HERE!!!
                             
                    #conn.sendall(clients)
                    
                    break;
                else: #failed to hash
                    conn.sendall('1'.encode('utf-8'))
                    break;
                
            else: #user is not present
                break;
        #conn.close()

    #def shareClients(self,conn):
        


        
    def user_is_present(self,user,psw,conn):
        is_present = False
        if user in self.identifier:
            if self.identifier[user] == psw:
                is_present = True
                conn.sendall('good userid, verifie the nonce'.encode('utf-8'))
            else:
                conn.sendall('wrong psw'.encode('utf-8'))
        else:
            data = 'wrong user name'
            conn.sendall(data)
        return is_present
        
        

class File:
    def __init__(self, filename): #addsection before add key
        self.filename = filename
        self.config = cp.ConfigParser(allow_no_value=True)
        self.file = open(self.filename,'r+')
        self.file.close()
        
    def addSection(self,section): #§ don't use
        self.config.add_section(section)
        with open(self.filename,'r+') as f:
            self.config.write(f)
            
    def getKey(self, section, key):
        self.config.read(self.filename)
        return self.config.get(section,key)
    def getListSection(self,section):
        self.config.read(self.filename)
        return list(self.config[section].keys())
    

    def addKey(self, section, key, value =None):
        self.config.set(section,key,value)
        with open(self.filename,'r+') as f:
            self.config.write(f)        

#s = Server1()
#s.launch_connection()
"""class TCPHandler(ss.BaseRequestHandler):
    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024)
       
        # just send back the same data, but upper-cased
        self.request.sendall(self.data.upper())"""
        
        
