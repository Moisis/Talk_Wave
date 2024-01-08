import colorama

import db


class ConfigServerThis:
    # # onlinePeers list for online account
    # onlinePeers = {}

    ##TODO Accounts
    # # accounts list for accounts
    accounts = {}
    # # tcpThreads list for online client's thread
    tcpThreads = {}

    rooms = {}
    # tcp and udp server port initializations
    def __init__(self):
        self.onlinePeers = {}
        print(colorama.Fore.GREEN+"Config started...")
        self.port = 15600
        self.portUDP = 15500

        # db initialization
        self.db = db.DB(True)

    def update_online_peer(self):
        self.onlinePeers = self.db.get_online_peers_usernames()
        return self.onlinePeers

    def update_available_chatrooms(self):
        self.availableChatrooms = self.db.get_available_chatrooms()
        return self.availableChatrooms
# Create an instance of the class
config_instance = ConfigServerThis()