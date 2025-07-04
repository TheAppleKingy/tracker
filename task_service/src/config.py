import os

from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), '..', '../.env')
load_dotenv(env_path)

DATABASE_URL = os.getenv('DATABASE_URL')
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")
FORMATTED_TEST_DATABASE_URL = os.getenv("FORMATTED_TEST_DATABASE_URL")
FORMATTED_DATABASE_URL = os.getenv("FORMATTED_DATABASE_URL")
SECRET_KEY = os.getenv('SECRET_KEY')
TOKEN_EXPIRE_TIME = eval(os.getenv('TOKEN_EXPIRE_TIME'))
