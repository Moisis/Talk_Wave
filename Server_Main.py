from socket import *
import select
import logging
from Server_Client_Thread import ClientThread
from Config import port, portUDP, tcpThreads


class Server_Main:
    # tcp and udp server port initializations
    print("Registy started...")
    # port = 15600
    # portUDP = 15500

    # # db initialization
    # db = db.DB()

    # gets the ip address of this peer
    # first checks to get it for windows devices
    # if the device that runs this application is not windows
    # it checks to get it for macos devices
    hostname = gethostname()
    try:
        host = gethostbyname(hostname)
    except gaierror:
        import netifaces as ni

        host = ni.ifaddresses('en0')[ni.AF_INET][0]['addr']

    print("Registry IP address: " + host)
    print("Registry port number: " + str(port))

    # # onlinePeers list for online account
    # onlinePeers = {}
    # # accounts list for accounts
    # accounts = {}
    # # tcpThreads list for online client's thread
    # tcpThreads = {}

    # tcp and udp socket initializations
    tcpSocket = socket(AF_INET, SOCK_STREAM)
    udpSocket = socket(AF_INET, SOCK_DGRAM)
    tcpSocket.bind((host, port))
    udpSocket.bind((host, portUDP))
    tcpSocket.listen(5)

    # input sockets that are listened
    inputs = [tcpSocket, udpSocket]

    # log file initialization
    logging.basicConfig(filename="registry.log", level=logging.INFO)

    # as long as at least a socket exists to listen registry runs
    while inputs:

        print("Listening for incoming connections...")
        # monitors for the incoming connections
        readable, writable, exceptional = select.select(inputs, [], [])
        for s in readable:
            # if the message received comes to the tcp socket
            # the connection is accepted and a thread is created for it, and that thread is started
            if s is tcpSocket:
                tcpClientSocket, addr = tcpSocket.accept()
                newThread = ClientThread(addr[0], addr[1], tcpClientSocket)
                Current_Peer_Port = addr[1]
                newThread.start()
                ##TODO
                tcpThreads[newThread.username] = newThread  # Store the client thread in a dictionary
            # if the message received comes to the udp socket
            elif s is udpSocket:
                # received the incoming udp message and parses it
                message, clientAddress = s.recvfrom(1024)
                message = message.decode().split()
                # checks if it is a hello message
                if message[0] == "HELLO":
                    # checks if the account that this hello message
                    # is sent from is online
                    if message[1] in tcpThreads:
                        # resets the timeout for that peer since the hello message is received
                        tcpThreads[message[1]].resetTimeout()
                        print("Hello is received from " + message[1])
                        logging.info(
                            "Received from " + clientAddress[0] + ":" + str(clientAddress[1]) + " -> " + " ".join(
                                message))

    # registry tcp socket is closed
    tcpSocket.close()


server_start = Server_Main()
