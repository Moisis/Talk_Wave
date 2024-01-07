import unittest
from pymongo import MongoClient
from db import DB

class TestDBOperations(unittest.TestCase):

    def setUp(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['Test-Talk-Wave']
        self.db_obj = DB()

    def test_register(self):
        username= "user"
        password = "pass"
        self.assertEqual(self.db_obj.is_account_exist(username),False)
        self.db_obj.register(username,password)
        self.assertEqual(self.db_obj.is_account_exist(username),True)


    def test_get_password(self):
        username = "user1"
        password = "pass1"
        self.db_obj.register(username, password)
        self.assertEqual(self.db_obj.get_password(username),password)


    def test_is_account_exist(self):
        username = "user2"
        password= "pass2"

        self.assertFalse(self.db_obj.is_account_exist(username))
        self.db_obj.register(username,password)
        self.assertTrue(self.db_obj.is_account_exist(username))


    def test_user_login_is_account_online(self):
        username = "user2"
        self.assertFalse(self.db_obj.is_account_online(username))
        self.db_obj.user_login(username,"127.0.0.1", "5522")
        self.assertTrue(self.db_obj.is_account_online(username))


    def test_user_logout(self):
        username = "user3"
        self.db_obj.user_login(username, "127.0.0.2", "5523")
        self.assertTrue(self.db_obj.is_account_online(username))
        self.db_obj.user_logout(username)
        self.assertFalse(self.db_obj.is_account_online(username))


    def test_get_peer_ip_port(self):
        username = "user6"
        self.db_obj.user_login(username, "127.0.1.3", "5555")
        self.assertEqual(self.db_obj.get_peer_ip_port(username),("127.0.1.3", "5555"))


    def test_get_available_chatrooms(self):
        self.assertEqual(self.db_obj.get_available_chatrooms(), [])
        # Register some chat rooms
        self.db_obj.register_room("room1","test1")
        self.db_obj.register_room("room2", "test2")
        self.assertEqual(self.db_obj.get_available_chatrooms(), ["room1", "room2"])
        collection = self.client["p2p-chat"]["rooms"]
        collection.drop()


    def test_register_room(self):
        roomId = "test_room"
        username = "tests-user"
        self.db_obj.register_room(roomId, username)
        self.assertTrue(self.db_obj.is_room_exist(roomId))
        collection = self.client["p2p-chat"]["rooms"]
        collection.drop()

    def test_get_first_peer(self):
        roomId = "test_room"
        self.assertIsNone(self.db_obj.get_first_peer(roomId))

        # Add a peer to the room
        self.db_obj.register_room(roomId, "test_user")
        self.assertEqual(self.db_obj.get_first_peer(roomId), "test_user")
        collection = self.client["p2p-chat"]["rooms"]
        collection.drop()


    def test_get_room_peers(self):
        roomId = "test_room1"
       # self.assertIsNone(self.db_obj.get_room_peers(roomId))

        # Add peers to the room
        self.db_obj.register_room(roomId, "test_user1")
        self.db_obj.join_room(roomId, "test_user2")
        self.assertEqual(self.db_obj.get_room_peers(roomId), ["test_user1", "test_user2"])
        collection = self.client["p2p-chat"]["rooms"]
        collection.drop()

    def test_join_and_leave_room(self):
        roomId = "test_room2"
        username = "test_user"
        username2 = "tests-user2"

        # Join the room
        self.db_obj.register_room(roomId, username2)
        self.db_obj.join_room(roomId, username)
        self.assertTrue(self.db_obj.find_room_peer(roomId, username))
        # Leave the room
        self.db_obj.leave_room(roomId, username)
        self.assertFalse(self.db_obj.find_room_peer(roomId, username))
        collection = self.client["p2p-chat"]["rooms"]
        collection.drop()

    def test_is_room_exist(self):
        ChatRoom_Name = "test_room3"
        self.assertFalse(self.db_obj.is_room_exist(ChatRoom_Name))

        # Register the chat room
        self.db_obj.register_room(ChatRoom_Name,"tests-user")
        self.assertTrue(self.db_obj.is_room_exist(ChatRoom_Name))
        collection = self.client["p2p-chat"]["rooms"]
        collection.drop()

    def test_delete_room(self):
        roomId = "test_room4"
        username = "admin_user"

        # Try to delete a non-existent room
        self.db_obj.delete_room(roomId, username)

        # Register the room and try to delete with a non-admin user
        self.db_obj.register_room(roomId,username)
        self.db_obj.join_room(roomId, "tests-user4")
        self.db_obj.delete_room(roomId, "tests-user4")

        # Delete the room with an admin user
        self.db_obj.join_room(roomId, username)
        self.db_obj.delete_room(roomId, username)
        self.assertFalse(self.db_obj.is_room_exist(roomId))
        collection = self.client["p2p-chat"]["rooms"]
        collection.drop()


    def test_find_room_peer(self):
        roomId= "tests-room"
        username = "test_user"
        self.db_obj.register_room(roomId, username)
        self.assertEqual(True,self.db_obj.find_room_peer(roomId,username))
        collection = self.client["p2p-chat"]["rooms"]
        collection.drop()

    def tearDown(self):
        self.client.drop_database('p2p-chat')

if __name__ == '__main__':
    unittest.main()
