import socket
import threading
import sqlite3

import config

import datetime

from pathlib import Path

#import ctypes

class colors:                  #   ANSII Escape Codes definition
 

    if config.config["ansi"] == "yes":
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

class Server:
    def __init__(self):
        self.start_server()

    def start_server(self):


        self.log_filename = 'chatroom' + datetime.datetime.now().strftime('%Y_%m_%d_%H%M%S') + '.log'     # Datetimestamp based filename
        self.log_file = open(config.config["logfolder"] + "\\" + self.log_filename, "w")                            # Creating a file
        self.log_file.write(datetime.datetime.now().strftime('**** Chatroom server started on %Y.%m.%d at %H:%M:%S.%f') + "\n")
        self.log_file.close()

        db_file = config.config["dbfilename"]

        # Check if database exists, if not then create one
        c_file = Path(db_file)
        if not c_file.is_file():        # Create Database

            sql = """ CREATE TABLE "users" (
	                    "username"	TEXT,
	                    "FirstName"	TEXT,
	                    "LastName"	TEXT,
	                    "Password"	TEXT,
	                    PRIMARY KEY("username")
            );"""

            try:
                conn = None                                         # Connect to SQLite
                conn = sqlite3.connect(db_file)
                cur = conn.cursor()
                cur.execute(sql)
                conn.commit()
                conn.close()
                print("Created new database file '" + colors.fYellow + db_file + colors.Reset + "'.")
                self.write_log("Created new database file '" + db_file + "'.")
            except:
                print(colors.fRed + "Cannot create database. Quitting." + colors.Reset)
                self.write_log("Cannot create database. Quitting.")
                quit()
            




        self.s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        
        host = config.config["host"]            # listening IP from config

        port = int( config.config["port"])

        self.clients = []

        self.s.bind((host,port))
        self.s.listen(100)


        # initialise logging
       
        self.write_log('Running on host: ' + str(host) + "\n")
        self.write_log('Running on port: ' + str(port) + "\n")
        



    
        print('Running on host: ' + str(host))
        print('Running on port: ' + str(port))


        self.username_lookup = {}
        self.connection_lookup = {}

        while True:
            c, addr = self.s.accept()
            
           

            while True:      # Initial Request
                try:
                    mess = c.recv(1024).decode().split('&')             # Get username & Password Hash from Client and parse the response
                
                    cmd = mess[0]
                    username = mess[1].lower()                          # Get username
                    pwd = mess[2]                                       # Get Password Hash
                

                    
                    conn = None                                         # Connect to SQLite
                    conn = sqlite3.connect(db_file)
                    cur = conn.cursor()

                    if cmd == "#l":           ################################## SIGN IN

                        cur.execute("select password from users where username=?",(username,)) # Get user's Password Hash
                        rows = cur.fetchall()

                        if len(rows)==0:                   # Zero result -> wrong username
                            c.send("#iBad".encode())        # Send back bad authentication
                        else:
                            row = rows[0]
                            if row[0]==pwd:                 # Password OK
                                c.send("#iOK".encode())
                                break
                            else:
                                c.send("#iBad".encode())    # Send back bad authentication
                    
                    if cmd == "#r":           #################################### SIGN ON 
                        firstname = mess[3]
                        lastname = mess[4]
                        try:                            
                            cur.execute("insert into users (username, FirstName, LastName, Password) values (?,?,?,?)", (username, firstname, lastname, pwd,))
                            conn.commit()
                            print("Created new user '" + colors.fYellow + username + colors.Reset + "'")
                            self.write_log("Created new user '" + username +  "'")
                            c.send(("New user '" + username + "' created.").encode())
                            break
                        except:
                            print("Cannot create new user '" + colors.fYellow + username + colors.Reset + "'. User exists.")
                            self.write_log("Cannot create new user '" + username +  "'. User exists.")
                            c.send(("ERROR creating new user '" + username + "'. User exists.").encode())
                            
                except:
                    print(colors.fRed + "Client closed connection prematurely." + colors.Reset)
                    self.write_log("Client closed connection prematurely.")
                    break

                # Successfull connection
                
            print(colors.fGreen+'New connection. Username: ' + colors.Reset+colors.fYellow+str(username) + colors.Reset)                    # Print log
            self.broadcast(colors.fGreen+'New person joined the room. Username: ' + colors.Reset+colors.fYellow+username + colors.Reset)    # Broadcast to others
            self.write_log('New connection. Username: ' + str(username))


            self.username_lookup[c] = username                                                                                           # Save username
            self.connection_lookup[username] = c                                                                                         # Save connection
            self.clients.append(c)          
                    
            threading.Thread(target=self.handle_client,args=(c,addr,)).start()
                                                                                                                # Save connection
                

    def write_log(self,msg):
        self.log_file = open(config.config["logfolder"] + "\\" + self.log_filename, "a")                            # Opening/Closing a file in order to avoid losing data
        self.log_file.write(datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S.%f") + " " + msg + "\n")
        self.log_file.close()


    def broadcast(self,msg):
        for connection in self.clients:
            connection.send(msg.encode())

    def handle_client(self,c,addr):
        while True:
            try:
                msg = c.recv(1024)
            except:
                c.shutdown(socket.SHUT_RDWR)
                self.clients.remove(c)
                
                print(colors.fYellow+str(self.username_lookup[c]) + colors.Reset+colors.fGreen + ' left the room.' + colors.Reset)
                self.broadcast(colors.fYellow+str(self.username_lookup[c]) + colors.Reset+colors.fGreen+' has left the room.' + colors.Reset)
                self.write_log(str(self.username_lookup[c]) + ' has left the chatroom.')

                break

            if msg.decode() != '':
                mm = msg.decode()
                u = mm.split(":")[0]    # user
                m = mm.split(":")[1]    # message
                print(colors.fYellow + u + ": " + colors.Reset+m)
                self.write_log(str(msg.decode()))
                # Check for the personal message
                pm = m.split("@")
                if len(pm)>1:   # There is '@'. Send personal message
                    pma = pm[1].split(' ')
                    au = pma[0] # addressee
                    try:
                        cc = self.connection_lookup[au]
                        cc.send(mm.encode())
                        print("Personal message sent to user '" + colors.fYellow + au + colors.Reset + "'")
                        self.write_log("Personal message sent to user '" + au + "'")                 
                    except:
                        print("User '" + colors.fYellow + au + colors.Reset + "' not found. Message '" + colors.fYellow + mm + colors.Reset + "' not sent.")
                        self.write_log("User '" + au + "' not found. Message '" + mm + "' not sent.")
                        c.send(("User '" + au + "' not found. Message not sent").encode())
                else:                                       # broadcast
                    for connection in self.clients:
                        if connection != c:                 # Send to everybody except self
                            connection.send(msg)



#ctypes.windll.kernel32.SetConsoleMode(ctypes.windll.kernel32.GetStdHandle(-11), 7)    # change the Windows 10 console mode to understand ANSII escape codes
server = Server()



