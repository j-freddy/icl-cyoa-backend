import json

import tornado
import tornado.web
import tornado.websocket

from src.models.gpt3 import GPT3Model
from src.gamebook_generator import GamebookGenerator
from src.text_generator import TextGenerator
from src.graph import GamebookGraph


class AuthBaseHandler(tornado.websocket.WebSocketHandler):  # noqa
    """Base class to define authentication methods"""

    async def get_email_from_auth(self):
        sess_id = self.get_secure_cookie("cyoa_session")
        if sess_id is None:
            return None

        user = await self.settings["db"]["login_credentials"].find_one(
            {"session_id": sess_id.decode()}, {"email": 1, "_id": 0}
        )

        if user is None:
            return None
        return user["email"]


class GenerateHandler(AuthBaseHandler):  # noqa
    """Simple Http handler to serve clients."""

    def check_origin(self, origin: str) -> bool:
        return True

    async def open(self):
        email = await self.get_email_from_auth()
        user = await self.settings["db"]["login_credentials"].find_one({
            "email": email,
        })
        self.api_key = user["api_key"]

    def on_message(self, json_msg):
        """
        Message received on channel
        """

        msg = json.loads(json_msg)

        req_type = msg["type"]
        data = msg["data"]

        generator = GamebookGenerator(TextGenerator(GPT3Model(self.api_key)))

        if req_type == "startNode":
            genre_prompt = data["prompt"]

            # Generates the first paragraph given a certain genre (passed from front end)
            # as well as the corresponding actions
            graph = generator.generate_start_from_genre(genre_prompt)

        elif req_type == "initialStory":

            initial_story_prompt = data["prompt"]

            graph = generator.generate_initial_story(initial_story_prompt)    

        else:
            graph = GamebookGraph.from_graph_dict(data["graph"])

        if req_type == "generateActions":
            node_to_expand = data["nodeToExpand"]
            generator.generate_actions_from_narrative(graph, node_to_expand)

        elif req_type == "generateNarrative":
            node_to_expand = data["nodeToExpand"]
            is_ending = data["isEnding"]
            descriptor = data["descriptor"]
            generator.generate_narrative_from_action(
                graph, 
                node_to_expand, 
                is_ending, 
                descriptor,
            )

        elif req_type == "connectNode":
            from_node = data["fromNode"]
            to_node = data["toNode"]

            generator.bridge_node(graph, from_node, to_node)

        self.write_message(json.dumps({"graph": graph.to_graph_dict()}))
