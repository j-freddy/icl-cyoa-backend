import json
import os
import uuid

import bson
import motor
import tornado
import tornado.web
from pymongo import ReturnDocument

from src.config import get_db_url, get_app_url
from src.models.gpt3 import GPT3Model
from src.gamebook_generator import GamebookGenerator
from src.text_generator import TextGenerator
from src.graph import GamebookGraph

LISTEN_PORT = os.getenv("PORT", 8000)
LISTEN_ADDRESS = "127.0.0.1"

client = motor.motor_tornado.MotorClient(get_db_url())
db = client.users


class BaseHandler(tornado.web.RequestHandler):  # noqa
    """Setting up the base headers for the handlers"""

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", get_app_url())
        self.set_header("Access-Control-Allow-Headers", "*")
        self.set_header("Access-Control-Allow-Credentials", "true")
        self.set_header("Access-Control-Max-Age", 1000)
        self.set_header("Content-type", "application/json")
        self.set_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.set_header(
            "Access-Control-Allow-Headers",
            "Content-Type, Access-Control-Allow-Origin, Access-Control-Allow-Headers,\
                             X-Requested-By, Access-Control-Allow-Methods",
        )

    def options(self):
        pass

    def get_current_user(self):
        return self.get_secure_cookie("user")


class AuthBaseHandler(BaseHandler):  # noqa
    """Base class to define authentication methods"""

    async def get_email_from_session(self):
        sess_id = self.get_secure_cookie("cyoa_session")
        if sess_id is None:
            return None

        user = await self.settings["db"]["login_credentials"].find_one(
            {"session_id": sess_id.decode()}, {"email": 1, "_id": 0}
        )

        if user is None:
            return None

        return user["email"]


class LoginHandler(AuthBaseHandler):  # noqa
    """Http handler to handle user authentication and profile databases fetching"""

    async def get(self):
        email = await self.get_email_from_session()

        if email is None:
            self.set_status(401)
            return
        print("logged in using session cookie")

        # write the email for display on the ui
        self.write(json.dumps({"email": email}))

    async def post(self):
        body = self.request.body
        credentials = json.loads(body)

        session_id: str = str(uuid.uuid4())
        # TODO: remove code duplication
        find_user = await self.settings["db"]["login_credentials"].find_one_and_update(
            {
                "email": credentials["email"],
                "password": credentials["password"],
            },
            {"$set": {"session_id": session_id}},
            return_document=ReturnDocument.AFTER,
        )
        if find_user is not None:
            print("login successful")
            self.set_secure_cookie(
                "cyoa_session", session_id, samesite="None", secure=True
            )
        else:
            print("no matching credentials!")
            self.set_status(401)


class UserStoriesHandler(AuthBaseHandler):  # noqa
    def get(self):
        ...

    async def post(self):
        email = await self.get_email_from_session()
        if email is None:
            self.set_status(401)
            return
        body = json.loads(self.request.body)
        req_type = body["type"]

        if req_type == "init":
            story_id: str = str(bson.ObjectId())
            _ = await self.settings["db"]["stories"].insert_one(
                {
                    "user_email": email,
                    "_id": story_id,
                    "name": "Story",
                    "story": {"nodes": []},
                }
            )
            self.write(json.dumps({"storyId": story_id}))

        elif req_type == "getStories":
            stories = self.settings["db"]["stories"].find({"user_email": email})
            # this is because you can't use an object of type MotorCursor in an 'await' expression, so you have to
            # iterate asynchronously.
            temp_story_list = []
            async for story in stories:
                temp_story_list.append(story)
            # TODO: remove this later, for debugging only
            #  TODO: make this cleaner
            story_list = [{"name": story["name"], "storyId": story["_id"]} for story in temp_story_list]
            self.write(json.dumps({"stories": story_list}))

        elif req_type == "saveName":
            story_id = body["storyId"]
            updated_name = body["name"]
            _ = await self.settings["db"]["stories"].find_one_and_update(
                {
                    "_id": story_id,
                },
                {"$set": {"name": updated_name}},
                return_document=ReturnDocument.AFTER,
            )

        elif req_type == "saveStory":
            story_id = body["storyId"]
            updated_story = body["story"]
            _ = await self.settings["db"]["stories"].find_one_and_update(
                {
                    "_id": story_id,
                },
                {"$set": {"story": updated_story}},
                return_document=ReturnDocument.AFTER,
            )

        elif req_type == "getStoryFromId":
            story_id = body["storyId"]
            story = await self.settings["db"]["stories"].find_one(
                {"_id": story_id}, {"_id": 0, "email": 0}
            )
            self.write(json.dumps(story))


class SignupHandler(BaseHandler):  # noqa
    async def post(self):
        body = self.request.body
        credentials = json.loads(body)
        credentials["_id"]: str = str(bson.ObjectId())
        credentials["session_id"]: str = str(uuid.uuid4())
        # TODO: remove code duplication, move db operations out to a separate method in base class

        user = await self.settings["db"]["login_credentials"].find_one(
            {
                "email": credentials["email"],
                "password": credentials["password"],
            }
        )
        if user is not None:
            print("credentials are already present, redirecting to login instead!")
            self.set_status(302)
        else:
            await self.settings["db"]["login_credentials"].insert_one(credentials)
            self.set_secure_cookie(
                "cyoa_session", credentials["session_id"], samesite="None", secure=True
            )
            print("added credentials to db!")


class RequestHandler(BaseHandler):  # noqa
    """Simple Http handler to serve clients."""

    def get(self):
        ...

    def post(self):
        """
        Message received on channel
        """
        json_msg = self.request.body

        msg = json.loads(json_msg)

        req_type = msg["type"]

        generator = GamebookGenerator(TextGenerator(GPT3Model()))

        data = msg["data"]

        if req_type == "startNode":

            genre_prompt = data["prompt"]

            # Generates the first paragraph given a certain genre (passed from front end)
            # as well as the corresponding actions
            graph = generator.generate_start_from_genre(genre_prompt)

        else:
            graph = GamebookGraph.from_graph_dict(data["graph"])

        if req_type == "generateActions":

            node_to_expand = data["nodeToExpand"]
            generator.generate_actions_from_narrative(graph, node_to_expand)

        elif req_type == "generateNarrative":

            node_to_expand = data["nodeToExpand"]
            generator.generate_narrative_from_action(graph, node_to_expand)

        elif req_type == "endNode":

            node_to_end = data["nodeToEnd"]

            # Ends current graph path
            generator.generate_narrative_from_action(graph, node_to_end, is_ending=True)

        elif req_type == "connectNode":

            from_node = data["fromNode"]
            to_node = data["toNode"]

            generator.bridge_node(graph, from_node, to_node)

        self.write(json.dumps({"graph": graph.to_graph_dict()}))


def main():
    app = tornado.web.Application(
        [
            (r"/", RequestHandler),
            (r"/login", LoginHandler),
            (r"/signup", SignupHandler),
            (r"/stories", UserStoriesHandler),
        ],
        db=db,
        debug=bool(os.getenv("DEV", False)),
        cookie_secret=os.getenv(
            "COOKIE_SECRET", "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__"
        ),
    )
    app.listen(int(LISTEN_PORT))
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
