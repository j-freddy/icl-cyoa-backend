import os
import motor
import tornado

from src.config import get_db_url
from src.server.account_handler import APIKeyHandler, LoginHandler, SignupHandler, UserStoriesHandler
from src.server.generate_handler import GenerateHandler

LISTEN_PORT = os.getenv("PORT", 8000)
LISTEN_ADDRESS = "127.0.0.1"

client = motor.motor_tornado.MotorClient(get_db_url())
db = client.users

def main():
    app = tornado.web.Application(
        [
            (r"/ws", GenerateHandler),
            (r"/login", LoginHandler),
            (r"/signup", SignupHandler),
            (r"/stories", UserStoriesHandler),
            (r"/key", APIKeyHandler),
        ],
        db=db,
        debug=bool(os.getenv("DEV", False)),
        cookie_secret=os.getenv(
            "COOKIE_SECRET", "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__"
        ),
        websocket_ping_interval=5,
    )
    app.listen(int(LISTEN_PORT))
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
