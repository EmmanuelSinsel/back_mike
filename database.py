import urllib
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker

load_dotenv()

class Database:
    engine = None

    def connection(self, database):
        server = str(os.getenv('DB_HOST')) + ":" + str(os.getenv('DB_PORT'))
        username = os.getenv('DB_USER')
        password = os.getenv('DB_PASSWORD')
        params = ("mysql+mysqlconnector://" + username + ":" + password +
                  "@" + server + "/" + database)
        print(params)
        self.engine = create_engine(params, echo=True, pool_size=10, max_overflow=20)
        db = sessionmaker(bind=self.engine)
        conn = db()
        return conn