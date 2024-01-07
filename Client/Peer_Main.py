import ast
import hashlib
from socket import *
import threading
import logging

import colorama
from colorama import Fore

from Peer_Server import PeerServer
from Peer_Client import PeerClient

from Config import config_instance


# main process of the peer
class peerMain:

    # peer initializations
    def __init__(self):

        colorama.init(autoreset=True)
        # ip address of the registry
        self.registryName = gethostname()
        # self.registryName = 'localhost'
        # port number of the registry
        self.registryPort = 15600
        # tcp socket connection to registry
        self.tcpClientSocket = socket(AF_INET, SOCK_STREAM)
        self.tcpClientSocket.connect((self.registryName, self.registryPort))
        # initializes udp socket which is used to send hello messages
        self.udpClientSocket = socket(AF_INET, SOCK_DGRAM)
        # udp port of the registry
        self.registryUDPPort = 15500
        # login info of the peer
        self.loginCredentials = (None, None)
        # online status of the peer
        self.isOnline = False
        # server port number of this peer
        self.peerServerPort = None
        # server of this peer
        self.peerServer = None
        # client of this peer
        self.peerClient = None
        # timer initialization
        self.timer = None

        # Track the users in the Chat Room
        self.ChatRoomUsers = []
        # Track the name of the Chat Room
        self.roomid = ''

        choice = "0"

        # log file initialization
        logging.basicConfig(filename="../peer.log", level=logging.INFO)

        try:
            # as long as the user is not logged out, asks to select an option in the menu
            while choice != "77":
                # menu selection prompt
                if not self.isOnline:
                    choice = input(colorama.Fore.CYAN +
                                   "Welcome!\nChoose: \n1.Create account\n2.Login\n77.Exit\n")
                else:

                    choice = input(colorama.Fore.CYAN +
                                   "Choose: \n1.Search\n2.Start a chat\n3.Show Online Users\n4.Create "
                                   "Chatroom\n5.Display available rooms\n6.Join Room\n7.Delete Room\n8.Leave "
                                   "Room\n9.Logout\n")
                # if choice is 1, creates an account with the username
                # and password entered by the user
                if choice == "1" and not self.isOnline:
                    username = input(colorama.Fore.LIGHTYELLOW_EX + "username: ")
                    password = input(colorama.Fore.LIGHTYELLOW_EX + "password: ")

                    self.createAccount(username, hashlib.sha3_256(password.encode()).hexdigest())
                # if choice is 2 and user is not logged in, asks for the username
                # and the password to login
                elif choice == "2" and not self.isOnline:
                    username = input(colorama.Fore.LIGHTYELLOW_EX + "username: ")
                    password = input(colorama.Fore.LIGHTYELLOW_EX + "password: ")

                    # assigns port to peer
                    sock = socket()
                    sock.bind(('', 0))
                    peerServerPort = sock.getsockname()[1]

                    status = self.login(username, hashlib.sha3_256(password.encode()).hexdigest(), peerServerPort)
                    # is user logs in successfully, peer variables are set
                    if status == 1:
                        self.isOnline = True
                        self.loginCredentials = (username, password)
                        self.peerServerPort = peerServerPort
                        # creates the server thread for this peer, and runs it
                        self.peerServer = PeerServer(self.loginCredentials[0], self.peerServerPort, self.roomid)
                        self.peerServer.start()
                        # hello message is sent to registry
                        self.sendHelloMessage()

                # if choice is 3 and user is logged in, then user is logged out
                # and peer variables are set, and server and client sockets are closed
                elif choice == "9" and self.isOnline:
                    self.logout(1)
                    self.isOnline = False
                    self.loginCredentials = (None, None)
                    self.peerServer.isOnline = False
                    self.peerServer.tcpServerSocket.close()
                    if self.peerClient is not None:
                        self.peerClient.tcpClientSocket.close()
                    print("Logged out successfully")
                # is peer is not logged in and exits the program
                elif choice == "77" and not self.isOnline:
                    self.logout(2)
                # if choice is 4 and user is online, then user is asked
                # for a username that is wanted to be searched
                elif choice == "1" and self.isOnline:
                    username = input(colorama.Fore.LIGHTYELLOW_EX + "Username to be searched: ")
                    searchStatus = self.searchUser(username, None)

                    # if user is found its ip address is shown to user
                    if searchStatus is not None and searchStatus != 0:
                        print("IP address of " + username + " is " + searchStatus)

                elif choice == "3" and self.isOnline:
                    config_instance.update_online_peer()
                    print(colorama.Fore.BLUE + "Online users:")
                    for item in config_instance.onlinePeers:
                        print(colorama.Fore.BLUE + item)

                # Handle chat room-related choices

                elif choice == "4" and self.isOnline:

                    roomId = input("Enter a Room ID: ")
                    # print(self.loginCredentials[0])
                    # self.createRoom(roomId, self.loginCredentials[0], self.peerServerPort)
                    self.createChatRoom(roomId)



                elif choice == "5" and self.isOnline:
                    config_instance.update_available_chatrooms()
                    print(colorama.Fore.BLUE + "Rooms:")
                    for item in config_instance.availableChatrooms:
                        print(colorama.Fore.BLUE + item)

                elif choice == "6" and self.isOnline:

                    ChatRoom_Name = input("Join Chat Room: ")
                    self.joinChatRoom(ChatRoom_Name)
                    while self.peerServer.inChatRoom:
                        message = input(f"{username}" + " : ")
                        self.ChatRoomUsers = self.updateChatRoomUsersList(ChatRoom_Name)
                        if self.ChatRoomUsers is not None:
                            if message == ":q":
                                self.leaveRoom(username, ChatRoom_Name)
                                break
                            else:
                                for user in self.ChatRoomUsers:
                                    # Don't send a message to the same user
                                    if user != username:
                                        self.Start_ChatRoom(user, message)



                elif choice == "7" and self.isOnline:
                    roomId = input("Enter a Room ID: ")
                    self.deleteRoom(roomId, username)
                    # print("Room Deleted Successfully\n")

                elif choice == "8" and self.isOnline:
                    roomId = input("Enter a Room ID: ")
                    self.leaveRoom(roomId, username)


                # if choice is 5 and user is online, then user is asked
                # to enter the username of the user that is wanted to be chatted
                elif choice == "2" and self.isOnline:
                    username = input(colorama.Fore.LIGHTYELLOW_EX + "Enter the username of user to start chat: ")
                    searchStatus = self.searchUser(username, None)
                    # if searched user is found, then its ip address and port number is retrieved
                    # and a client thread is created
                    # main process waits for the client thread to finish its chat
                    if searchStatus is not None and searchStatus != 0:
                        searchStatus = searchStatus.split(":")
                        self.peerClient = PeerClient(searchStatus[0], int(searchStatus[1]), self.loginCredentials[0],
                                                     self.peerServer, None, "allo")

                        self.peerClient.start()
                        self.peerClient.join()
                # if this is the receiver side then it will get the prompt to accept an incoming request during the main loop
                # that's why response is evaluated in main process not the server thread even though the prompt is printed by server
                # if the response is ok then a client is created for this peer with the OK message and that's why it will directly
                # sent an OK message to the requesting side peer server and waits for the user input
                # main process waits for the client thread to finish its chat
                elif choice == "OK" and self.isOnline:
                    okMessage = "OK " + self.loginCredentials[0]
                    logging.info("Send to " + self.peerServer.connectedPeerIP + " -> " + okMessage)
                    self.peerServer.connectedPeerSocket.send(okMessage.encode())
                    self.peerServer.inChatRoom = False
                    self.peerClient = PeerClient(self.peerServer.connectedPeerIP, self.peerServer.connectedPeerPort,
                                                 self.loginCredentials[0], self.peerServer, "OK", "ALOOOO")

                    self.peerClient.start()
                    self.peerClient.join()
                # if user rejects the chat request then reject message is sent to the requester side
                elif choice == "REJECT" and self.isOnline:
                    self.peerServer.connectedPeerSocket.send("REJECT".encode())
                    self.peerServer.isChatRequested = 0
                    logging.info("Send to " + self.peerServer.connectedPeerIP + " -> REJECT")
                # if choice is cancel timer for hello message is cancelled
                elif choice == "CANCEL":
                    self.timer.cancel()
                    break
            # if main process is not ended with cancel selection
            # socket of the client is closed
            if choice != "CANCEL":
                self.tcpClientSocket.close()


        except KeyboardInterrupt:
            # Handle KeyboardInterrupt (Ctrl+C) gracefully
            print("Received KeyboardInterrupt. Logging out...")
            self.logout(1)  # Logout with option 1
            self.isOnline = False
            self.loginCredentials = (None, None)
            self.peerServer.isOnline = False
            self.peerServer.tcpServerSocket.close()
            if self.peerClient is not None:
                self.peerClient.tcpClientSocket.close()
            print("Logged out successfully")


        finally:
            # Cleanup code (if any) that should run regardless of an exception
            self.tcpClientSocket.close()

    # account creation function
    def createAccount(self, username, password):
        # join message to create an account is composed and sent to registry
        # if response is success then informs the user for account creation
        # if response is exist then informs the user for account existence
        message = "JOIN " + username + " " + password
        logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        logging.info("Received from " + self.registryName + " -> " + response)
        if response == "join-success":
            print(colorama.Fore.GREEN + "Account created...")
        elif response == "join-exist":
            print(colorama.Fore.RED + "choose another username or login...")

    # login function
    def login(self, username, password, peerServerPort):
        # a login message is composed and sent to registry
        # an integer is returned according to each response
        message = "LOGIN " + username + " " + password + " " + str(peerServerPort)
        logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        logging.info("Received from " + self.registryName + " -> " + response)
        if response == "login-success":
            print(colorama.Fore.GREEN + "Logged in successfully...")
            return 1
        elif response == "login-account-not-exist":
            print(colorama.Fore.RED + "Account does not exist...")
            return 0
        elif response == "login-online":
            print("Account is already online...")
            return 2
        elif response == "login-wrong-password":
            print(colorama.Fore.RED + "Wrong password...")
            return 3

    # logout function
    def logout(self, option):
        # a logout message is composed and sent to registry
        # timer is stopped
        if option == 1:
            message = "LOGOUT " + self.loginCredentials[0]
            self.timer.cancel()
        else:
            message = "LOGOUT"
        logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(message.encode())

    # function for searching an online user
    def searchUser(self, username, mode):
        # a search message is composed and sent to registry
        # custom value is returned according to each response
        # to this search message
        message = "SEARCH " + username
        logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode().split()
        logging.info("Received from " + self.registryName + " -> " + " ".join(response))
        if mode == "Chat-Room":
            if response[0] == "search-success":
                return response[1]
            elif response[0] == "search-user-not-online":
                return 0
            elif response[0] == "search-user-not-found":
                return None
        else:
            if response[0] == "search-success":
                print(username + " is found successfully...")
                return response[1]
            elif response[0] == "search-user-not-online":
                print(username + " is not online...")
                return 0
            elif response[0] == "search-user-not-found":
                print(username + " is not found")
                return None

    def updateChatRoomUsersList(self, ChatRoom_Name):
        if self.isOnline:
            # Send a request to the registry to get the Chat Room  Users update
            message = "Get_ChatRoom_UsersList " + ChatRoom_Name
            self.tcpClientSocket.send(message.encode())
            response = self.tcpClientSocket.recv(1024).decode().split()
            # Process the received chat room list
        if response[0] == "ChatRoom_Userlist":
            updatedChatRoomUsersList = response[1:]
            return updatedChatRoomUsersList

    def Start_ChatRoom(self, username, message):
        SearchStatus = self.searchUser(username, "Chat-Room")
        # if searched user is found, then its ip address and port number is retrieved
        # and a client thread is created
        # main process waits for the client thread to finish its chat
        if SearchStatus is not None:
            SearchStatus = SearchStatus.split(":")
            self.peerClient = PeerClient(SearchStatus[0], int(SearchStatus[1]), self.loginCredentials[0],
                                         self.peerServer, None, "ChatRoom", message, username)
            self.peerClient.start()
            self.peerClient.join()

    # Function for creating a Chat Room
    def createChatRoom(self, ChatRoom_Name):
        message = "CREATE-ROOM " + ChatRoom_Name
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode().split()
        if response[0] == "chat-room-exist":
            print(f"{colorama.Fore.RED}This Chat Room {ChatRoom_Name} already exist Try Again ")
            return 0
        elif response[0] == "create-room-success":
            print(f"{colorama.Fore.YELLOW}The Chat Room {ChatRoom_Name} is created Successfully ")

        # Function for Joining a Chat Room

    def joinChatRoom(self, ChatRoom_Name):
        message = "JOIN-ROOM " + ChatRoom_Name + " " + self.loginCredentials[0]
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode().split()
        if response[0] == "room-not-exist":
            print(f"{colorama.Fore.YELLOW} Chat Room {ChatRoom_Name} is not found")
            return 0
        elif response[0] == "join-success":
            print(f"{colorama.Fore.YELLOW} Joined Chat Room {ChatRoom_Name} successfully\n")
            self.peerServer.inChatRoom = True
            self.roomid = ChatRoom_Name
            # This for loop is for showing the users in Chat Room
            print(f"{colorama.Fore.CYAN}Current Online users in this Chat Room {ChatRoom_Name} are : \n")

            for user in (self.updateChatRoomUsersList(ChatRoom_Name)):
                print(f"{colorama.Fore.CYAN}{user}")
                self.ChatRoomUsers.append(user)
            if self.ChatRoomUsers != None:
                for user in self.ChatRoomUsers:
                    self.Start_ChatRoom(user,
                                        f"User {self.loginCredentials[0]} has joined the {ChatRoom_Name} Chat Room")
        elif response == "join-exist":
            print("you are already in chatroom")

    def leaveRoom(self, username, ChatRoom_Name):
        if self.ChatRoomUsers != None:
            for user in self.ChatRoomUsers:
                self.Start_ChatRoom(user, f"{colorama.Fore.RED}User {username} has left the room")
        message = "LEAVE-ROOM " + username + " " + ChatRoom_Name
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode().split()
        if response[0] == "leave-success":
            print(f"{colorama.Fore.RED} You have left the chat room")
            self.peerServer.inChatroom = False
            self.peerServer.mode2 = "aloo"
            return 0
        elif response == "leave-not-valid":
            print("You are not in this chatroom")

    def deleteRoom(self, roomId, username):
        message = "DELETE-ROOM " + roomId + " " + username
        logging.info("Send to " + self.registryName + ":" + str(self.registryPort) + " -> " + message)
        self.tcpClientSocket.send(message.encode())
        response = self.tcpClientSocket.recv(1024).decode()
        logging.info("Received from " + self.registryName + " -> " + response)
        if response == "delete-room-success":
            print("Chat Room Deleted Successfully.")
        elif response == "room-not-exist":
            print("Chat Room Doesn't Exist")
        elif response == "delete-room-denied":
            print("You have no access to delete this room.")

    # function for sending hello message
    # a timer thread is used to send hello messages to udp socket of registry
    def sendHelloMessage(self):
        message = "HELLO " + self.loginCredentials[0]
        logging.info("Send to " + self.registryName + ":" + str(self.registryUDPPort) + " -> " + message)
        self.udpClientSocket.sendto(message.encode(), (self.registryName, self.registryUDPPort))
        self.timer = threading.Timer(1, self.sendHelloMessage)
        self.timer.start()


# peer is started
main = peerMain()
