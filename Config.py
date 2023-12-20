import db


class ConfigServerThis:
    # # onlinePeers list for online account
    # onlinePeers = {}

    ##TODO Accounts
    # # accounts list for accounts
    accounts = {}
    # # tcpThreads list for online client's thread
    tcpThreads = {}

    # tcp and udp server port initializations
    def __init__(self):
        self.onlinePeers = {}
        print("Config started...")
        self.port = 15600
        self.portUDP = 15500

        # db initialization
        self.db = db.DB()

    def update_online_peer(self):
        self.onlinePeers = self.db.get_online_peers_usernames()
        return self.onlinePeers


# Create an instance of the class
config_instance = ConfigServerThis()