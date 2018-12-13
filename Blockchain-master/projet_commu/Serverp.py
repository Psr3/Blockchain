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
def file_op(file):
    return open(file,'w')
    

class Server1:
    
    def __init__(self,port,filename):
        self.file = open('next.ini','w')
        self.config = cp.ConfigParser(allow_no_value=True)
        self.set_file()
        self.ip_address = self.get_info('node','ip_adress')
        self.port = port
        self.serverSocket = so.socket(so.AF_INET,so.SOCK_STREAM)
        self.serverSocket.bind((self.ip_address,port))
        self.serverSocket.listen(6)
        self.identifier = {'alice':'ecila','jb':'bj'}
        #on met les identifiant ici???
        
    def launch_connection(self): #launch TCP server
        #tcp_serv = ss.TCPServer((self.ip_address,self.port),TCPHandler)
        while 1:
            self.connectionSocket, self.addr = self.serverSocket.accept()
            td.start_new_thread(self.handle_message_client,(self.connectionSocket,))
        
    def handle_message_client(self,conn):
        while 1:
            conn = self.connectionSocket
            conn.sendall('entre user and psw'.encode('utf-8'))
            use_psw = conn.recv(1024)
            #print(len(str(use_psw.decode('utf-8'))))
            user_id = use_psw.split()#list of string
            print(user_id[0].decode('utf-8'))
            #psw = use_psw.split() #string
            
            if self.user_is_present(user_id[0].decode('utf-8'),user_id[1].decode('utf-8'),conn)==True:
                nonce  = str(dt.datetime.now().year) + str(dt.datetime.now().month) + str(dt.datetime.now().day) + str(dt.datetime.now().hour)+str(dt.datetime.now().minute)+str(dt.datetime.now().second)
                conn.sendall(nonce.encode('utf-8'))
                
                hash_nonce = hl.sha256((nonce +user_id[1].decode('utf-8')).encode('utf-8')).hexdigest() #string
                hashed_nonce = conn.recv(1024)
                print(hashed_nonce.decode('utf-8'))
                print(hash_nonce)
                if hash_nonce ==hashed_nonce.decode('utf-8'):
                    conn.sendall('success u in tha server'.encode('utf-8'))
                    
                    
                    break;
                else:
                    conn.sendall('error u out tha server'.encode('utf-8'))
                    break;
                
            else:
                break;
        conn.close()
            
        
            
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
    
    def set_file(self):
        self.config['node'] = {}
        self.config['neighbour'] = {}
        self.config.write(self.file)
            
    def get_info(self,section,key):
        self.config.read(self.file)
        return self.config.get(section,key)
        
        
        
            
class File:
    def __init__(self, filename): #addsection before add key
        self.filename = filename
        self.config = cp.ConfigParser(allow_no_value=True)
        self.file = open(self.filename,'w')
        self.file.close()
        
    def addSection(self,section):
        self.config.add_section(section)
        with open(self.filename,'w') as f:
            self.config.write(f)
            
    def getKey(self, section, key):
        self.config.read(self.filename)
        return self.config.get(section,key)

    def addKey(self, section, key, value =None):
        self.config.set(section,key,value)
        with open(self.filename,'w') as f:
            self.config.write(f)
        
s = Server1(5000,'con.ini')
#s.launch_connection()
"""class TCPHandler(ss.BaseRequestHandler):
    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024)
       
        # just send back the same data, but upper-cased
        self.request.sendall(self.data.upper())"""
        
        
