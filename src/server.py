import asyncio
import json
import os

import tornado
import tornado.web

from src.models.gpt3 import GPT3Model
from src.text_generator import GamebookTextGenerator
from src.tree import GamebookTree

LISTEN_PORT = os.getenv('PORT', 8000)
LISTEN_ADDRESS = "127.0.0.1"


class RequestHandler(tornado.web.RequestHandler):  # noqa
    """Simple WebSocket handler to serve clients."""

    def post(self):
        """
        Message received on channel
        """
        json_msg = self.request.body

        msg = json.loads(json_msg)

        req_type = msg["type"]

        if req_type == "expandNode":
            data = msg["data"]

            graph = GamebookTree.from_nodes_dict_list(data["nodes"])
            node_to_expand = data["nodeToExpand"]

            GamebookTextGenerator(GPT3Model()).expand_graph_once(graph, node_to_expand)
            # example serialization
            self.write(json.dumps({"nodes": graph.to_nodes_dict_list()}))

            # TODO: need to generate and send back a graph with expanded node - using text_generator
        elif req_type == "endNode":
            data = msg["data"]

            graph = GamebookTree.from_nodes_dict_list(data["nodes"])
            node_to_end = data["nodeToEnd"]

            # Ends current graph path
            GamebookTextGenerator(GPT3Model()).expand_graph_once(graph, node_to_end, True)
            
            self.write(json.dumps({"nodes": graph.to_nodes_dict_list()}))

        else:
            self.close()

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Content-type', 'application/json')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header('Access-Control-Allow-Headers',
                        'Content-Type, Access-Control-Allow-Origin, Access-Control-Allow-Headers,\
                             X-Requested-By, Access-Control-Allow-Methods')

    def options(self):
        pass

def main():
    app = tornado.web.Application([
        (r"/", RequestHandler),
    ])
    app.listen(LISTEN_PORT)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()
