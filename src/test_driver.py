import unittest
import db.driver as driver


class DBDriverUnittest(unittest.TestCase):
    def test_local_client(self):
        try:
            client = driver.MongoDriver.get_client()
            client.list_database_names()

        except Exception:
            self.fail()


if __name__ == "__main__":
    unittest.main()
