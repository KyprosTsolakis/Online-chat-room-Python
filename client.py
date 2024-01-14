import socket
import threading
import sys
import hashlib
import getpass 
import client_config



class colors:                  #   ANSII Escape Codes definition
 
    if client_config.config["ansi"] == "yes":
        fBlack      = '\u001b[30;1m'
        fRed        = '\u001b[31;1m'
        fGreen      = '\u001b[32;1m'
        fYellow     = '\u001b[33;1m'
        fBlue       = '\u001b[34;1m'
        fMagenta    = '\u001b[35;1m'
        fCyan       = '\u001b[36;1m'
        fWhite      = '\u001b[37;1m'
        
        bBlack      = '\u001b[40;1m'
        bRed        = '\u001b[41;1m'
        bGreen      = '\u001b[42;1m'
        bYellow     = '\u001b[43;1m'
        bBlue       = '\u001b[44;1m'
        bMagenta    = '\u001b[45;1m'
        bCyan       = '\u001b[46;1m'
        bWhite      = '\u001b[47;1m'
        Clear       = '\u001b[2J'
        Reset       = '\u001b[0m'
    else:
        fBlack      = ''
        fRed        = ''
        fGreen      = ''
        fYellow     = ''
        fBlue       = ''
        fMagenta    = ''
        fCyan       = ''
        fWhite      = ''
        
        bBlack      = ''
        bRed        = ''
        bGreen      = ''
        bYellow     = ''
        bBlue       = ''
        bMagenta    = ''
        bCyan       = ''
        bWhite      = ''
        Clear       = ''
        Reset       = ''

class Client:
    def __init__(self):
        self.create_connection()

    def create_connection(self):


        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)


 ########################################   CONNECTING TO THE SERVER ############################       
        while True:                         
            try:
                host = client_config.config["host"]             # Read host from configuration
                port = int(client_config.config["port"])        # Read port from configuration

                self.s.connect((host,port))
                print(colors.fGreen+"Connected to host: "+colors.fYellow+host+colors.Reset)
                print(colors.fGreen+"Port: "+colors.fYellow+str(port)+colors.Reset)
                input("Press Enter to continue...")
                break
            except:
                print(colors.fRed+"Couldn't connect to server "+colors.fYellow+host+":"+str(port)+colors.Reset)
                input("Press Enter to continue...")


########################################   MENU  ############################       

        while True:
        
            print (colors.Clear)
            print (colors.fYellow)
            
            print('Sign in to the chatroom -------------------- 1')
            print('Sign on to the chatroom -------------------- 2')
            print('Quit --------------------------------------- Q')
            print (colors.Reset)

            cc = input(colors.fGreen+"Select your option and press Enter > "+colors.Reset)
       
            if cc=="1":
                ########################################   LOGIN (LOOP UNTIL SUCCESSFUL LOGIN) ############################        
                while True:
                    self.username = input(colors.fGreen+'Enter username --> '+colors.Reset)
                    self.password=getpass.getpass(colors.fGreen+'Enter password --> '+colors.Reset)
                    h = hashlib.sha256()
                    h.update(self.password.encode())
                    self.password = h.hexdigest()
                    self.s.send(("#l&"+self.username + "&" + self.password).encode())     # Send password to the server
                    try:
                        resp = self.s.recv(1204).decode()
                    except:
                        print("Connection closed")


                        break

                    if resp=="#iOK":
                        break
                    else:
                        self.r = input(colors.fRed+'Wrong username or password. Press Enter to continue'+colors.Reset)
                break

            if cc=="2":
                ########################################   LOGIN (LOOP UNTIL SUCCESSFUL LOGIN) ############################        
                self.username = input(colors.fGreen+'Enter username --> '+colors.Reset)         # Get username
                self.firstname = input(colors.fGreen+'Enter First Name --> '+colors.Reset)         # Get first name
                self.lastname = input(colors.fGreen+'Enter Last Name --> '+colors.Reset)         # Get last name

                while True:                                                                     # Get password. Loop until they match
                    self.password=getpass.getpass(colors.fGreen+'Enter password --> '+colors.Reset)
                    self.password1=getpass.getpass(colors.fGreen+'Confirm password --> '+colors.Reset)
                    if self.password == self.password1:
                        break
                    else:
                        print(colors.fRed+"Passwords do not match!"+colors.Reset)
                
                h = hashlib.sha256()
                h.update(self.password.encode())
                self.password = h.hexdigest()
                self.s.send(("#r&"+self.username + "&" + self.password + "&" + self.firstname + "&" + self.lastname).encode())     # Send credentials to the server
                resp = self.s.recv(1204).decode()
                if resp[0:5]=="ERROR":
                    print(colors.fRed + resp + colors.Reset)
                    input(colors.fRed + "Press ENTER to continue..." + colors.Reset)
                else:
                    print(colors.fGreen + resp + colors.Reset)
                    break
                

            if cc=="Q":
                quit()
                break

            input(colors.fRed+"Wrong input. Press Enter to continue."+colors.Reset)



######################  CHAT MESSAGE PROCESSING ###############################################################

        print(colors.fYellow+"You are connected to the chatroom. Type your message."+colors.Reset)


        message_handler = threading.Thread(target=self.handle_messages,args=())
        message_handler.start()


        input_handler = threading.Thread(target=self.input_handler,args=())
        input_handler.start()
    
    

    def handle_messages(self):
        while True:
            try:
                print(self.s.recv(1204).decode())
            except:

                print("Connection closed")
                break
        quit()        

    def input_handler(self):
        while True:
           # si = input(colors.fYellow+self.username+': '+ colors.Reset)
            si = input()
            if si[0]=="#":        # this is command
                if si[1].capitalize()=="Q":
                    self.s.close()
                    break
            self.s.send((self.username+': '+si).encode())


client = Client()

