import json
import os
import uuid

import bson
import motor
import tornado
import tornado.web
import tornado.websocket
from pymongo import ReturnDocument

from src.config import get_db_url, get_app_url
from src.models.gpt3 import GPT3Model
from src.gamebook_generator import GamebookGenerator
from src.text_generator import TextGenerator
from src.graph import GamebookGraph


class WebBaseHandler(tornado.web.RequestHandler):  # noqa
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


class AuthBaseHandler(WebBaseHandler):  # noqa
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

        user = await self.settings["db"]["login_credentials"].find_one({
                "email": email,
            })
        # write the email for display on the ui
        api_key = user["api_key"]
        self.write(json.dumps({"email": email, "apiKey": api_key}))

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
        api_key = find_user["api_key"]
        self.write(json.dumps({"apiKey": api_key}))


class SignupHandler(AuthBaseHandler):  # noqa
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


class APIKeyHandler(AuthBaseHandler):

    async def get(self):
        email = await self.get_email_from_session()
        if email is None:
            self.set_status(401)
            return
        user = await self.settings["db"]["login_credentials"].find_one({
            "email": email,
        })
        return user["api_key"]

    async def post(self):
        email = await self.get_email_from_session()
        if email is None:
            self.set_status(401)
            return
        body = json.loads(self.request.body)
        api_key = body["apiKey"]
        await self.settings["db"]["login_credentials"].find_one_and_update(
            {
                "email": email,
            },
            {"$set": {"api_key": api_key}},
            return_document=ReturnDocument.AFTER,
        )


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
            story_list = []
            for story in temp_story_list:
                firstParagraph = "ATTENTION: First paragraph of story not yet generated."
                totalSections = len(story["story"]["nodes"])
                if story["story"]["nodes"]:
                    firstParagraph = story["story"]["nodes"][0]["data"]
                story_list.append({"name": story["name"], "storyId": story["_id"], "firstParagraph": firstParagraph, "totalSections": totalSections})
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
            if story["user_email"] == email:
                self.write(json.dumps(story))
            else:
                self.set_status(403)
        
        elif req_type == "deleteStoryFromId":
            story = await self.settings["db"]["stories"].find_one(
                {"_id": story_id}, {"_id": 0, "email": 0}
            )
            if story["user_email"] == email:
                _ = await self.settings["db"]["stories"].delete_one(
                {"_id": story_id}
                )
            else:
                self.set_status(403)


class SignupHandler(WebBaseHandler):  # noqa
    async def post(self):
        body = self.request.body
        credentials = json.loads(body)
        credentials["_id"]: str = str(bson.ObjectId())
        credentials["session_id"]: str = str(uuid.uuid4())
        credentials["api_key"] = ""
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
