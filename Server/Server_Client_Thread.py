
import uuid
import threading
import logging

from Server_UDP_Server import UDPServer
from Config import config_instance



# This class is used to process the peer messages sent to registry
# for each peer connected to registry, a new client thread is created
class ClientThread(threading.Thread):
    # initializations for client thread
    def __init__(self, ip, port, tcpClientSocket):
        threading.Thread.__init__(self)
        # ip of the connected peer
        self.ip = ip
        # port number of the connected peer
        self.port = port
        # socket of the peer
        self.tcpClientSocket = tcpClientSocket
        # username, online status and udp server initializations

        ##todo
        # self.username = None
        self.username = str(uuid.uuid4())
        self.isOnline = True
        self.udpServer = None

        print("New thread started for " + ip + ":" + str(port))

    # main of the thread
    def run(self):
        # locks for thread which will be used for thread synchronization
        self.lock = threading.Lock()
        print("Connection from: " + self.ip + ":" + str(config_instance.port))
        print("IP Connected: " + self.ip)

        while True:
            try:
                # waits for incoming messages from peers
                message = self.tcpClientSocket.recv(1024).decode().split()
                logging.info("Received from " + self.ip + ":" + str(self.port) + " -> " + " ".join(message))
                #   JOIN    #
                if message[0] == "JOIN":
                    # join-exist is sent to peer,
                    # if an account with this username already exists
                    if config_instance.db.is_account_exist(message[1]):
                        response = "join-exist"
                        print("From-> " + self.ip + ":" + str(self.port) + " " + response)
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())
                    # join-success is sent to peer,
                    # if an account with this username is not exist, and the account is created
                    else:
                        config_instance.db.register(message[1], message[2])
                        # db.register(message[1] ,  hashlib.sha3_256(message[2].encode()).hexdigest())
                        response = "join-success"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())
                #   LOGIN    #
                elif message[0] == "LOGIN":
                    # login-account-not-exist is sent to peer,
                    # if an account with the username does not exist
                    if not  config_instance.db.is_account_exist(message[1]):
                        response = "login-account-not-exist"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())
                    # login-online is sent to peer,
                    # if an account with the username already online
                    elif  config_instance.db.is_account_online(message[1]):
                        response = "login-online"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())
                    # login-success is sent to peer,
                    # if an account with the username exists and not online
                    else:
                        # retrieves the account's password, and checks if the one entered by the user is correct
                        retrievedPass =  config_instance.db.get_password(message[1])
                        # if password is correct, then peer's thread is added to threads list
                        # peer is added to db with its username, port number, and ip address
                        if retrievedPass == message[2]:
                            self.username = message[1]
                            self.lock.acquire()
                            try:
                                config_instance.tcpThreads[self.username] = self
                            finally:
                                self.lock.release()
                            ##todo

                            config_instance.db.user_login(message[1], self.ip, message[3])
                            ## db.user_login(message[1], self.ip, hashlib.sha3_256(message[3].encode()).hexdigest())
                            # login-success is sent to peer,
                            # and a udp server thread is created for this peer, and thread is started
                            # timer thread of the udp server is started
                            response = "login-success"
                            logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                            self.tcpClientSocket.send(response.encode())
                            self.udpServer = UDPServer(self.username, self.tcpClientSocket)
                            self.udpServer.start()
                            self.udpServer.timer.start()
                        # if password not matches and then login-wrong-password response is sent
                        else:
                            response = "login-wrong-password"
                            logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                            self.tcpClientSocket.send(response.encode())
                #   LOGOUT  #
                elif message[0] == "LOGOUT":
                    # if user is online,
                    # removes the user from onlinePeers list
                    # and removes the thread for this user from tcpThreads
                    # socket is closed and timer thread of the udp for this
                    # user is cancelled
                    if len(message) > 1 and message[1] is not None and config_instance.db.is_account_online(message[1]):
                        config_instance.db.user_logout(message[1])
                        self.lock.acquire()
                        try:
                            if message[1] in config_instance.tcpThreads:
                                del config_instance.tcpThreads[message[1]]
                        finally:
                            self.lock.release()
                        print(self.ip + ":" + str(self.port) + " is logged out")
                        self.tcpClientSocket.close()
                        self.udpServer.timer.cancel()
                        break
                    else:
                        self.tcpClientSocket.close()
                        break

                # CREATE ROOM #
                elif message[0] == "CREATE-ROOM":
                # CREATE-exist is sent to peer if a room with this username already exists
                    if config_instance.db.is_room_exist(message[1]):
                        response = "chat-room-exist"
                        print("From-> " + self.ip + ":" + str(self.port) + " " + response)
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())
                    else:
                        config_instance.db.register_room(message[1], message[2])
                        response = "create-room-success"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())

                # JOIN ROOM #
                elif message[0] == "JOIN-ROOM":
                    print("Welcome!")
                    roomId = message[1]
                    print(f"RoomID = {roomId}")

                    if config_instance.db.is_room_exist(roomId):

                        config_instance.db.join_room(roomId, message[2])
                        response = "join-success"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + str(response))
                        self.tcpClientSocket.send(response.encode())

                    else:
                        response = "join-exist"
                        print("From-> " + self.ip + ":" + str(self.port) + " " + response)
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())



                # DELETE #
                elif message[0] == "DELETE-ROOM":
                    if not config_instance.db.is_room_exist(message[1]):
                        response = "chat-room-not-exist"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())
                    else:
                        config_instance.db.delete_room(message[1])
                        response == "delete-room-success"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())

                #   SEARCH  #
                elif message[0] == "SEARCH":
                    # checks if an account with the username exists
                    if config_instance.db.is_account_exist(message[1]):
                        # checks if the account is online
                        # and sends the related response to peer
                        if config_instance.db.is_account_online(message[1]):
                            peer_info = config_instance.db.get_peer_ip_port(message[1])
                            response = "search-success " + peer_info[0] + ":" + peer_info[1]
                            logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                            self.tcpClientSocket.send(response.encode())
                        else:
                            response = "search-user-not-online"
                            logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                            self.tcpClientSocket.send(response.encode())
                    # enters if username does not exist
                    else:
                        response = "search-user-not-found"
                        logging.info("Send to " + self.ip + ":" + str(self.port) + " -> " + response)
                        self.tcpClientSocket.send(response.encode())
            except OSError as oErr:
                logging.error("OSError: {0}".format(oErr))

                # function for resettin the timeout for the udp timer thread

    def resetTimeout(self):
        self.udpServer.resetTimer()
