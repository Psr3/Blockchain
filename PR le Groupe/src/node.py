import socket as so
import hashlib as hl
import datetime as dt
import threading as td
import time
import dill as pk
import authentication_center as sv#file correspond to module :(
class Client:
    def __init__(self):
        self.file = sv.File('config/client.ini')
                   
        self.file.addSection('neighbour')
        self.user = self.file.getKey('node','username')
        self.psw = self.file.getKey('registration','secret')
        self.ip_c = self.file.getKey('node','ip_address')
        self.clientSocket = so.socket(so.AF_INET, so.SOCK_STREAM)
        self.timetowait = 1
        self.clientSocket.settimeout(self.timetowait)
        self.isActiv = False
        self.out = False
        self.hasRecv = False

        # SOCKET FOR SERVER ACTIVITY OF THE NODE
        self.port_p = 5001
        self.serverSocket = so.socket(so.AF_INET,so.SOCK_STREAM)
        self.serverSocket.bind((self.ip_c,self.port_p))
        self.serverSocket.listen(10)


        self.reg_to_server()

        

        self.lock = td.RLock()
        recv = td.Thread(name='REC THREAD', target = self.recvAddr, args = ())
        recv.setDaemon(True)
        
        recv_blo = td.Thread(name='RECBOCK THREAD', target = self.recvBlock, args = ())
        recv_blo.setDaemon(True)
        recv.start()
        recv_blo.start()
        #self.recvBlock()


    def recver(self,conn):
        leng = conn.recv(1024)
        if leng=='chain'.encode():
            return leng
        else:
            l =int(leng.decode())
            data = b''
            while l>0:
                recv = conn.recv(1024)
                data = data +recv
                lr = len(recv)
                l = l-lr
            self.lock.acquire()
            a=len(data)
            if int(leng.decode()) == a:
                conn.sendall('ok'.encode())
                self.lock.release()
                return data
            else:
                return b''
        
            
            
            
    def closeAll(self,val):
        self.clientSocket.send(('out ' +self.ip_c).encode())
        self.clientSocket.close()
        self.file.deleteSec('neighbour')
        self.isActiv = not(val)
        self.out = not(val)
        
    def broadCast(self): # send when cliq submit
        if self.isActiv ==True: 
            if self.file.getListSection('neighbour')!=0: #PAS SEUL
                blc = self.chain.getLastBlock()
                for node in self.file.getListSection('neighbour'):
                    try:
                        soc = so.socket(so.AF_INET, so.SOCK_STREAM)
                        soc.connect((node,self.port_p))
                        to_send = pk.dumps(blc)
                        l = str(len(to_send))
                        soc.sendall(l.encode())
                        soc.sendall(to_send)
                        ack = soc.recv(1024).decode()
                        while ack!='ok':
                            l = str(len(to_send))
                            soc.sendall(l.encode())
                            soc.sendall(to_send)
                            ack = soc.recv(1024).decode()
                        soc.close()
                    except so.timeout:
                        print('BROADCAST TIMEOUT'+str(self.timetowait))
                    except so.error:
                        print('SOERROR Broadcast()')
            else: #seul
                pass
                #self.chain.addBlock(blc = blc)
            
        else:
            print('isActiv= FALSE')
        
    def recvBlock(self): #chain? TOURNE EN ARRIERE PLAN
        recvchain =False
        if self.isActiv ==True: #has reg to server
            while self.hasRecv ==False: #first time to connect ==RECV chain
                clientSocket = so.socket(so.AF_INET, so.SOCK_STREAM)
                time.sleep(1)#let Time for recvAddr to get IP
                self.listSec = self.file.getListSection('neighbour')
                self.lock.acquire()
                if len(self.listSec)!=0: #PAS SEUL
                    clientSocket.connect((self.listSec[len(self.listSec)-1],self.port_p))#connect au dernier
                    clientSocket.sendall('chain'.encode()) #WHO GONNA SEND THIS CHAIN

                    chain =self.recver(clientSocket) #clientSocket.recv(1024)
                    self.chain = pk.loads(chain)
                    recvchain = True
                    self.hasRecv =True
                else: #s'il est seul ==>create chain
                    self.chain = BlockChain()
                    self.hasRecv =True
                    recvchain= True
        self.lock.release()
        while recvchain:
            if self.out ==True:
                self.serverSocket.close()
                recvchain = False
            self.sockChain,self.addrChain = self.serverSocket.accept()
            hand = td.Thread(name='HANDLEBLOC', target = self.handle_bloc, args = (self.sockChain,))
            hand.setDaemon(True)
            hand.start()
                
    def handle_bloc(self,conn):
        
        bloc_p = self.recver(conn)#conn.recv(1024)
        if bloc_p =='chain'.encode(): #send the chain
            chain_to = pk.dumps(self.chain)
            l = str(len(chain_to))
            conn.sendall(l.encode())
            conn.sendall(chain_to)
            ack = conn.recv(1024).decode()
            while ack!='ok':
                conn.sendall(l.encode())
                conn.sendall(chain_to)
                ack = conn.recv(1024).decode()
            
            self.sockChain.close()
            
        else: #it's just==> add to your chain
            bloc = pk.loads(bloc_p)
            self.chain.addrecvBlock(bloc)
            self.sockChain.close()
            
        
    def asking_chain(self):
        self.hasRecv = False

    
    def reg_to_server(self):
        ip_s = self.file.getKey('registration','ip_address')
        port_s = 5001
        self.clientSocket.connect((ip_s,port_s))
        self.clientSocket.recv(1024)#ASKING TO SEND USER AND PSW
        
        self.clientSocket.send((self.user + ' ' +self.psw).encode('utf-8'))
        sent = self.clientSocket.recv(1024).decode('utf-8')#RECV IF USER IS OR NOT
        print(sent)
        try:
            nonce = self.clientSocket.recv(1024).decode('utf-8')
            ash = hl.sha256((nonce+self.psw).encode('utf-8')).hexdigest()
            self.clientSocket.send(ash.encode('utf-8'))
        
            statut = self.clientSocket.recv(1024).decode('utf-8')
            if statut =='0':#connection sucess
                self.isActiv = True
            else:
                res = False
        except so.timeout:
            print('VERIFY USER AND PSW')
        
    def getIsActiv(self):
        return self.isActiv


    def recvAddr(self):
        
        while True:
            if self.isActiv ==False:
                break
            try:
                print('checking for new client: WAIT '+str(self.timetowait)+' sec ...\n' )
                new = self.clientSocket.recv(1024).decode()
            except so.timeout:
                print('not new client since '+str(self.timetowait)+' sec\n')
            except so.error:
                pass
            else:
                self.lock.acquire()
                try:
                    try:
                        notif_out = new.split()
                        if new not in self.file.getListSection('neighbour'):
                            if len(notif_out)>1:
                                for key in notif_out:
                                    if key!='out' and key!=self.ip_c:
                                        self.file.addKey('neighbour',key)
                                        
                            elif len(notif_out)==1:
                                if notif_out[0]!='out' and notif_out[0]!=self.ip_c:
                                    self.file.addKey('neighbour',notif_out[0])
                    except IndexError:
                        pass
                except KeyError:
                    print('KEYYYY')
                try:    
                    if notif_out[0] == 'out':
                        print(notif_out[0],notif_out[1])
                        print(notif_out[1])
                        self.file.deleteKey('neighbour',notif_out[1])
                except IndexError:
                    pass
                self.lock.release()
    def getChain(self):
        return self.chain
            
class Block: #str et repr just for print the object
    def __init__(self):
        
        self.tim = str(dt.datetime.now().year) + str(dt.datetime.now().month) + str(dt.datetime.now().day) + str(dt.datetime.now().hour)+str(dt.datetime.now().minute)+str(dt.datetime.now().second)

    def __repr__(self):
        return 'id = {}, amount = {}, time = {}, hash = {}, prevHash = {} {}'.format(str(self.id),self.data,self.tim,self.hash,self.prevHash,'-------')
    def getPrevHash(self):
        return self.prevHash
    def getHash(self):
        return self.hash
    def getData(self):
        return str(self.data)
    def getIndex(self):
        return str(self.id)
    def getTime(self):
        return self.tim
    def setHash(self):
        
        self.hash = hl.sha256((self.id+self.data+self.tim).encode('utf-8')).hexdigest()
    def setPrevHash(self,prev):
        self.prevHash = str(prev)
    def setIndex(self,a):
        self.id = str(a)
    def setData(self,data):
        self.data = str(data)+'$'
        
class BlockChain: #for the genesis block we decided for the previous hash
    def __init__(self): # SEE OBJECTF:2 CONSTRUCTOR ?
        self.chain = []

    def __str__(self):
        return str(self.chain)
    
    def addBlock(self,blc =None):
        if blc!= None:
            block = Block()
            if len(self.chain)==0: #first BLOCK
                block.setPrevHash(0)
                block.setData(blc)
                block.setIndex(0)
                block.setHash()
                self.chain.append(block)
            else:
                block.setPrevHash(self.getLastBlock().getHash())
                block.setData(blc)
                block.setIndex(len(self.chain))
                block.setHash()
                self.chain.append(block)

    def addrecvBlock(self,blc):
        self.chain.append(blc)
        
    def getLastBlock(self):
        return self.chain[-1]
    def getSizeChain(self):
        return len(self.chain)
    def chainIsValid(self):
        res = True
        for i in range(1,len(self.chain)):
            if self.chain[i].getPrevHash() != self.chain[i-1].getHash():
                res = False
                return res
            else:
                res = True
        return res

    def getBlock(self,i):
        return self.chain[i]

from tkinter import *


class Window:
    def __init__(self):
        self.client = Client()
        
        self.window = Tk()
        self.window.title("BlockChain")



                       
        self.window.columnconfigure(5, weight=2)         
        

        
        # Create labels
        self.enter = StringVar()
        Label(self.window, textvariable = self.enter).grid(sticky =  N,columnspan = 3)
        Label(self.window, text = "Amount").grid(row = 1, column =5,padx= 5,pady=5, sticky =  W+ E)
        self.valid =  StringVar()
        Label(self.window, textvariable = self.valid).grid(row = 5, column = 2,padx= 5,pady=5, sticky =  W+ E)
        """self.look =  StringVar()
        Label(self.window, textvariable = self.look).grid(row = 5, column = 1, sticky =  W)
        Label(self.window, text = 'Type out to leave').grid(row = 6, column = 1, sticky =  W+E)"""
        # Create entries
        self.amount =  StringVar()
        Entry(self.window, textvariable = self.amount, justify = RIGHT).grid(row = 2, column = 5)
    
        
       

        #button
        Button(self.window, text = 'Submit', command = self.Submit).grid(row = 3,column = 5, padx= 5,pady=5, sticky=  W+ E)

        Button(self.window, text = "Chain Valid ?", command = self.validate).grid(row = 4, column = 5, padx= 5,pady=5, sticky = W+ E)
        Button(self.window, text = "See the chain", command = self.see).grid(row = 6, column = 5, padx= 5,pady=5, sticky = W+ E+S+N)
        Button(self.window, text = 'Clique to logout', command = self.destroy).grid(row = 7,column = 5, padx= 5,pady=5, sticky=  W+ E)
        self.exit = StringVar()

       
        time.sleep(2) #wait for the thread to creat chain
        self.chain = self.client.getChain()
        self.window.protocol("WM_DELETE_WINDOW",self.destroy)
        self.window.geometry('600x600')
        self.window.mainloop()

    def Submit(self):
        mon = self.amount.get()
        if mon == '':
            self.enter.set('PROVIDE AMOUNT')
        else:
            self.enter.set('YOU had ' + mon +'$' +' in the chain')
            self.chain.addBlock(blc = mon)
            if self.chain.chainIsValid()==True:
                self.client.broadCast()
            else:
                self.enter.set('YOU Have an invalid block')
                self.client.asking_chain() #reasking the chain to 
        
   
    def validate(self):
        if self.chain.chainIsValid()==True:
            self.valid.set('CHAIN IS VALID')
        else:
            self.valid.set('CHAIN IS NOT VALID')
    def see(self): #FUNCTION TO DISPLAY WHAT's NEED TO BE SEE
        scroll = Scrollbar(self.window)
        scroll.grid(row = 8,column = 9,sticky = N+S+E+W)
        
        txt = Text(self.window,height = 9, width = 30)

        
        txt.grid(row = 8,columnspan = 8,sticky=W+ E+S+N)
        scroll.config(command=txt.yview)
        txt.config(yscrollcommand=scroll.set,relief = RAISED)
        for i in range(self.chain.getSizeChain()):
            bl = self.chain.getBlock(i)
            q = ('BLOC{} ==> id = '+str(bl.getIndex()) +',' +  ' data = ' + str(bl.getData()) +
                 ',' + 'timestamp =  '+ str(bl.getTime())+ ',' +' hash = ' +str(bl.getHash()) +',' +'prevHas ='+ str(bl.getPrevHash())+ '----\n').format(i)
                                            
            txt.insert(END,q)
        txt.config(state = 'disable')
    def destroy(self):
        try:
            self.client.closeAll(True)
            self.window.destroy()
        except:
              pass
            


if __name__ == '__main__':
    Window()
