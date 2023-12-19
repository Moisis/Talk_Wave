import db

# onlinePeers list for online account
onlinePeers = {}
# accounts list for accounts
accounts = {}
# tcpThreads list for online client's thread
tcpThreads = {}

# tcp and udp server port initializations
print("Config started...")
port = 15600
portUDP = 15500

# db initialization
db = db.DB()
