import os
import subprocess
import pymongo
from urllib.parse import quote_plus


class MongoDriver:
    _CLIENT = None

    @classmethod
    def get_client(cls):
        return cls._get_local_client()

    @classmethod
    def _get_local_client(cls):
        if not cls._CLIENT:
            # Define the command
            command = ["brew", "services", "start", "mongodb-community@7.0"]

            # Execute the command
            subprocess.run(command, check=True)

            cls._CLIENT = pymongo.MongoClient(
                f'mongodb://{os.environ["bn_local_user"]}:{quote_plus(os.environ["bn_local_password"])}@127.0.0.1:27017/?authSource=admin'
            )

            try:
                cls._CLIENT.list_database_names()

            except Exception as e:
                raise RuntimeError(f"Error connecting to local Mongo: {e}")

        return cls._CLIENT


if __name__ == "__main__":
    print(MongoDriver.get_client().list_database_names())
