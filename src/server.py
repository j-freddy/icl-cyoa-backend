import json
import os

import tornado.websocket

from src.models.gpt3 import GPT3Model
from src.text_generator import GamebookTextGenerator
from src.tree import GamebookTree

LISTEN_PORT = os.getenv("PORT", 8000)
LISTEN_ADDRESS = "127.0.0.1"


class WebSocketHandler(tornado.websocket.WebSocketHandler):  # noqa
    """Simple WebSocket handler to serve clients."""

    @classmethod
    def urls(cls):
        return [
            (r"/ws/(.*)", cls, {}),
        ]

    def open(self, channel: str):
        self.channel = channel
        print(f"websocket opened, channel: {channel}")

    def on_close(self):
        print("websocket closed")

    def on_message(self, json_msg: str):
        """
        Message received on channel
        """
        msg = json.loads(json_msg)

        req_type = msg["type"]

        if req_type == "expandNode":
            data = msg["data"]

            graph = GamebookTree.from_nodes_dict_list(data["nodes"])
            node_to_expand = data["nodeToExpand"]

            GamebookTextGenerator(GPT3Model()).expand_graph_once(graph, node_to_expand)
            # example serialization
            self.write_message(json.dumps({"nodes": graph.to_nodes_dict_list()}))

            # TODO: need to generate and send back a graph with expanded node - using text_generator
        else:
            self.close()

    def check_origin(self, origin):
        """
        Override the origin check if needed
        """
        return True


def main():
    app = tornado.web.Application(WebSocketHandler.urls())

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(LISTEN_PORT)

    # Start IO/Event loop
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    # TODO: construct a text generator with a model
    main()
