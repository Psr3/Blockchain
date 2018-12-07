# -*- coding: utf-8 -*-
"""
Created on Thu Nov 29 21:02:22 2018

@author: Utilisateur
"""
import socket as so
import hashlib as hl
import datetime as dt
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
            clients = self.clientSocket.recv(1024)
            clients = pickle.loads(clients)
            print(clients)
            
        else:
            res = False
        #self.clientSocket.close() move up

    def isActiv(self):#not in use
        car = input('quit or stay:')
        activ = True
        if car=='quit':
            activ = False
            self.clientSocket.send('quit'.encode())
            self.clientSocket.close()
        else:
            activ = True
        return activ

    def transfert(self): #transfert money
        if self.isActiv == True:
            while True:
                car = input('type out or set amount you to transfert (you can set index pos'+'\nbut you risk to invalided the chain) :')
                if car == 'out':
                    self.clientSocket.send('out'.encode()) 
                    self.clientSocket.close()
                    break
                else:
                    #print(car[0])
                    #print(car[1])
                    print (len(car))
                    self.chain.addBlock(car[0], int(car[2]))
                    print (self.chain)
        else:
            print('regist to server befor add money')



    
            
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
            else: #add at that index and +1 for the other
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
            print(i)
            print(self.chain[i].getPrevHash())
            print(self.chain[i-1].getHash())
            if self.chain[i].getPrevHash() != self.chain[i-1].getHash():
                res = False
                print(i)
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

