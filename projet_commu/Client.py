# -*- coding: utf-8 -*-
"""
Created on Thu Nov 29 21:02:22 2018

@author: Utilisateur
"""
import socket as so
import hashlib as hl
class Client1:
    
    def __init__(self,user,psw,ip_c,port_c):
        """self.ip_s = ip_s
        self.port_s = port_s"""
        self.user = user
        self.psw = psw
        self.ip_c = ip_c
        self.port_c= port_c
        self.clientSocket = so.socket(so.AF_INET, so.SOCK_STREAM)
        self.clientSocket.bind((ip_c,port_c))
        
    def reg_to_server(self,ip_s,port_s):
        self.clientSocket.connect((ip_s,port_s))
        self.clientSocket.recv(1024)
        
        self.clientSocket.send((self.user + ' ' +self.psw).encode('utf-8'))
        sent = self.clientSocket.recv(1024)#if
        print(sent)
        nonce = self.clientSocket.recv(1024).decode('utf-8')
        ash = hl.sha256((nonce+self.psw).encode('utf-8')).hexdigest()
        self.clientSocket.send(ash.encode('utf-8'))
        
        last = self.clientSocket.recv(1024).decode('utf-8')
        print(last)
        self.clientSocket.close()

c = Client1('jb','bj','169.254.187.121',5000)
c.reg_to_server('169.254.240.185',5000)
