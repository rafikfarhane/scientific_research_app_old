import unittest
import database


class TestingDatabase(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super(TestingDatabase, self).__init__(methodName)
        self.db = database.Database()
        self.con_login = self.db.create_connection(self.db.login_db)
        self.all_users_db = self.db.create_connection(self.db.all_users_db)
        
    def test_register_user(self):
        result = self.db.register_user(self.con_login, "LukasP", "test8@gmail.com", "starkesPasswort")
        self.assertTrue(result)

    def  test_login(self):
        result = self.db.login_user(self.con_login, "LukasD", "starkesPasswort")
        self.assertTrue(result)
        
    def  test_search_user(self):
        result = self.db.search_user("LukasP", "test8@gmail.com")
        self.assertTrue(result)
        

if __name__ == "__main__":
    unittest.main()
