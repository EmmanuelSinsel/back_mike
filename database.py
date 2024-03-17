import urllib
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker

load_dotenv()

class Database:
    server = str(os.getenv('DB_HOST')) + ":" + str(os.getenv('DB_PORT'))
    database = os.getenv('DB_DATABASE')
    username = os.getenv('DB_USER')
    password = os.getenv('DB_PASSWORD')
    params = ("mysql+mysqlconnector://"+username+":"+password+
              "@"+server+"/"+database)

    engine = create_engine(params, echo=True)

    def connection(self):
        db = sessionmaker(bind=self.engine)
        conn = db()
        return conn