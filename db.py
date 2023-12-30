from pymongo import MongoClient


# Includes database operations
class DB:
    # db initializations
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['p2p-chat']

    def get_online_peers_usernames(self):
        result_cursor = self.db.online_peers.find({"username": {"$exists": True}})
        usernames = [doc['username'] for doc in result_cursor]
        return usernames

    # checks if an account with the username exists
    def is_account_exist(self, username):
        user_exists = self.db.accounts.find_one({'username': username})
        if user_exists is not None:
            return True
        else:
            return False

    # registers a user
    def register(self, username, password):
        account = {
            "username": username,
            "password": password
        }
        self.db.accounts.insert_one(account)

    # retrieves the password for a given username
    def get_password(self, username):
        return self.db.accounts.find_one({"username": username})["password"]

    # checks if an account with the username online
    def is_account_online(self, username):
        if self.db.online_peers.count_documents({"username": username}) > 0:
            return True
        else:
            return False

    # logs in the user
    def user_login(self, username, ip, port):
        online_peer = {
            "username": username,
            "ip": ip,
            "port": port
        }
        self.db.online_peers.insert_one(online_peer)

    # logs out the user
    def user_logout(self, username):
        self.db.online_peers.delete_one({"username": username})

    # retrieves the ip address and the port number of the username
    def get_peer_ip_port(self, username):
        res = self.db.online_peers.find_one({"username": username})
        return res["ip"], res["port"]

    def is_room_exist(self, roomId):
        return bool(self.db.rooms.find_one({'roomId': roomId}))

    def register_room(self, roomId, username):

    # Check if the roomId already exists in the database
        if self.db.rooms.find_one({"roomId": roomId}):
            raise ValueError(f"Room with id {roomId} already exists.")
        room = {
            "roomId": roomId,
            "peers": [username]
        }
        self.db.accounts.update_one({"username": username}, {"$push": {"roomId": roomId}})
        self.db.rooms.insert_one(room)


    def get_first_peer(self, roomId):
        room = self.db.rooms.find_one({"roomId": roomId})
        # Check if the room exists and has the 'peers' field
        if room and 'peers' in room:
            # Return the first element of the 'peers' field
            return room['peers'][0]

        # Return None or handle the case where the room or 'peers' field doesn't exist
        return None    # Store the room information in the database
    def get_available_chatrooms(self):
        result_cursor = self.db.rooms.find({"roomId": {"$exists": True}})
        chatrooms = [doc['roomId'] for doc in result_cursor]
        return chatrooms

    def join_room(self, roomId, username):  # add members to chatroom and update if new peer joined
        self.db.rooms.update_one(
            {"roomId": roomId}, {"$push": {"peers": username}})
        self.db.accounts.update_one(
            {"username": username}, {"$push": {"rooms": roomId}})


    def delete_room(self, roomId, username):
        # Check if the roomId exists in the database
        existing_room = self.db.rooms.find_one({"roomId": roomId})
        if not username == self.get_first_peer(roomId):
            print(f"{username} has no access to delete {roomId}.")

        elif existing_room:
            # Delete the room from the database
            self.db.rooms.delete_one({"roomId": roomId})
            print(f"Room with id {roomId} has been deleted.")
        else:
            print(f"Room with id {roomId} does not exist.")
