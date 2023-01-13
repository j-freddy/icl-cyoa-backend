import json

import tornado
import tornado.web
import tornado.websocket

from src.models.gpt3 import GPT3Model, OpenAIRateLimitError, OpenAIUnavailableError
from src.gamebook_generator import GamebookGenerator, GenerationProgressFeedback
from src.text_generator import TextGenerator, GenerationError
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

class GenerateHandler(AuthBaseHandler, GenerationProgressFeedback):  # noqa
    """Simple Http handler to serve clients."""

    def check_origin(self, origin: str) -> bool:
        return True

    async def open(self):
        email = await self.get_email_from_auth()
        user = await self.settings["db"]["login_credentials"].find_one({
            "email": email,
        })
        if user is None:
            self.close()
        else:
            self.api_key = user.get("api_key", None)
            if self.api_key == "":
                self.api_key = None

    def on_message(self, json_msg):
        """
        Message received on channel
        """
        try:
            msg = json.loads(json_msg)

            req_type = msg["type"]
            data = msg["data"]
            temperature = msg["temperature"]

            generator = GamebookGenerator(TextGenerator(GPT3Model(self.api_key, temperature=temperature)))

            if req_type == "initialStory":
                initial_story_prompt = data["prompt"]

                graph = generator.generate_initial_story(initial_story_prompt)    

            else:
                graph = GamebookGraph.from_graph_dict(data["graph"])

            if req_type == "generateActions":
                node_to_expand = data["nodeToExpand"]
                generator.generate_actions_from_narrative(graph, node_to_expand)

            elif req_type == "addAction":
                node_to_expand = data["nodeToExpand"]
                num_new_actions = data["numNewActions"]
                generator.add_actions(graph, node_to_expand, num_new_actions=num_new_actions)

            elif req_type == "generateNarrative":
                node_to_expand = data["nodeToExpand"]
                is_ending = data["isEnding"]
                descriptor = data["descriptor"]
                details = data["details"]
                style = data["style"]

                generator.generate_narrative_from_action(
                    graph, 
                    node_to_expand, 
                    is_ending, 
                    descriptor,
                    details,
                    style
                )

            elif req_type == "connectNode":
                from_node = data["fromNode"]
                to_node = data["toNode"]

                generator.bridge_node(graph, from_node, to_node)

            elif req_type == "generateMany":
                from_node: int = data["fromNode"]
                max_depth: int = data["maxDepth"]
                # save_to_id = msg["saveToId"]

                generator.generate_many(graph, from_node, max_depth, self)

                # TODO Save graph to id

            self.write_message(json.dumps({
                "resType": "requestComplete", 
                "graph": graph.to_graph_dict(),
            }))

        except OpenAIRateLimitError:
            self.write_message(json.dumps({
                "resType": "rateLimitError", 
            }))

        except OpenAIUnavailableError:
            self.write_message(json.dumps({
                "resType": "openaiError", 
            }))

        except GenerationError:
            self.write_message(json.dumps({
                "resType": "nlpParseError", 
            }))

    def send_generation_update(
        self,
        graph: GamebookGraph,
        num_nodes_generated: int,
        percentage: float
    ):
        self.write_message(json.dumps({
            "resType": "progressUpdate",
            "graph": graph.to_graph_dict(),
            "numNodesGenerated": num_nodes_generated,
            "percentage": percentage,
        }))
