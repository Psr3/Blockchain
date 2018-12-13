# -*- coding: utf-8 -*-
"""
Created on Thu Nov 29 21:02:22 2018

@author: Utilisateur
"""
import socket as so
import hashlib as hl
import datetime as dt
import threading as td
import select
import time
import pickle
import Server as sv#file correspond to module :(
class Client1:
    #logout msg is out
    def __init__(self):
        self.file = sv.File('client.ini')
        self.user = self.file.getKey('node','username')
        self.psw = self.file.getKey('registration','secret')
        self.ip_c = self.file.getKey('node','ip_address')
        #self.port_c= port_c
        self.clientSocket = so.socket(so.AF_INET, so.SOCK_STREAM)
        #self.clientSocket.bind((ip_c,port_c))automatic
        self.a = []
        self.chain = BlockChain()
        self.isActiv = False
        
    def reg_to_server(self):
        ip_s = self.file.getKey('registration','ip_address')
        port_s = 5001
        self.clientSocket.connect((ip_s,port_s))
        self.clientSocket.recv(1024)
        
        self.clientSocket.send((self.user + ' ' +self.psw).encode('utf-8'))
        sent = self.clientSocket.recv(1024).decode('utf-8')#if
        print(sent)
        nonce = self.clientSocket.recv(1024).decode('utf-8')
        ash = hl.sha256((nonce+self.psw).encode('utf-8')).hexdigest()
        self.clientSocket.send(ash.encode('utf-8'))
        
        statut = self.clientSocket.recv(1024).decode('utf-8')
        if statut =='0':#connection sucess
            self.isActiv = True
            """clients = self.clientSocket.recv(1024)
            clients = pickle.loads(clients)
            print(clients)"""
            
        else:
            res = False
    def getIsActiv(self):
        return self.isActiv

    def transfert(self): #transfert money #in use GOTTA CHANGE THIS
        global lock
        lock = td.Lock()
        if self.isActiv == True: #STUCK HERE
            while True:
                recv = td.Thread(name='receving thread',target=self.recvAddr, args=(self.clientSocket,))
                car = input('type out or set amount you to transfert (you can set index pos'+'\nbut you risk to invalided the chain) :')
                if car == 'out':
                    self.clientSocket.send(('out ' +self.ip_c).encode()) #???
                    self.isActiv = False
                    
                    self.clientSocket.close()
                    break
                else:
                    
                    amount,index = car.split()
                    trans = td.Thread(name='chain thread',target=self.createChain, args=(amount,int(index)))
                    recv.start()
                    trans.start()
                    """recv.join()
                    trans.join()"""
                    """ad = self.clientSocket.recv(1024)
                    amount,index = car.split()
                    self.chain.addBlock(amount, index)
                    print (ad)"""
        else:
            print('regist to server befor add')
    def recvAddr(self,conn):
        global lock
        """time.sleep(3)
        r, _, _ = select.select([conn], [], [])
        if r:
            data = conn.recv(1024)
            print(data)"""
        
        try:
            a = conn.recv(1024).decode()
            self.file.addKey('neighbour',a)
            notif_out = a.split()
            if notif_out[0] == 'out':
                print(notif_out[0],notif_out[1])
                self.file.deleteKey('neighbour',notif_out[1])
                
        except ConnectionAbortedError as e:
            print ('EEEEEEEEEEEEEEEEEEEEEEE')
            raise
        

    def createChain(self,somme,index):
        self.chain.addBlock(somme,index)
	
            
class Block: #str et repr just for print the object
    def __init__(self):
        """self.id = str(index)
        self.data = str(data) + '$'"""
        self.time = str(dt.datetime.now().year) + str(dt.datetime.now().month) + str(dt.datetime.now().day) + str(dt.datetime.now().hour)+str(dt.datetime.now().minute)
        """self.prevHash =prevHash
        self.setHash()"""
    def __repr__(self):
        return str((str(self.id),str(self.data),self.hash,self.prevHash))
    def getPrevHash(self):
        return self.prevHash
    def getHash(self):
        return self.hash
    def getData(self):
        return str(self.data)
    def getIndex(self):
        return str(self.id)
    
    def setHash(self):
        self.hash = hl.sha256((self.id+self.data+self.time).encode('utf-8')).hexdigest()
    
    def setPrevHash(self,prev):
        self.prevHash = str(prev)
    def setIndex(self,a):
        self.id = str(a)
    def setData(self,data):
        self.data = str(data)+'$'
        
class BlockChain: #for the genesis block we decided for the previous hash
    def __init__(self):
        self.chain = []

    def __str__(self):
        return str(self.chain)
    
    def addBlock(self,data,index = None):
        block = Block()
        if len(self.chain)==0:
            block.setPrevHash(0)
            block.setData(data)
            block.setIndex(0)
            block.setHash()
            self.chain.append(block)
        
        else:
            if index ==None: #we add to the end
                block.setPrevHash(self.getLastBlock().getHash())
                block.setIndex(len(self.chain))
                block.setData(data)
                block.setHash()
                self.chain.append(block)
            else: #add at that index and do +1 for the other
                block.setPrevHash(self.chain[index-1].getHash())
                block.setIndex(index)
                block.setData(data)
                block.setHash()
                self.chain.insert(index,block)
                for i in range(index+1,len(self.chain)):
                    self.chain[i].setIndex(i)
        
    def getLastBlock(self):
        return self.chain[-1]
    
    def chainIsValid(self):
        res = True
        for i in range(1,len(self.chain)):
            print(self.chain[i].getPrevHash())
            print(self.chain[i-1].getHash())
            if self.chain[i].getPrevHash() != self.chain[i-1].getHash():
                res = False
                return res
            else:
                res = True
        return res
"""b= BlockChain()
b.addBlock(5)
b.addBlock(6)
b.addBlock(9)
b.addBlock(3,)
print(b)
#b.chainIsValid()
print (b.chainIsValid())"""
c = Client1()
c.reg_to_server()
c.transfert()

