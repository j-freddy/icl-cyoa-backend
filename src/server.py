import asyncio
import json
import os

import tornado
import tornado.web

from src.models.gpt3 import GPT3Model
from src.gamebook_generator import GamebookGenerator
from src.text_generator import TextGenerator
from src.graph import GamebookGraph

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
        
        generator = GamebookGenerator(TextGenerator(GPT3Model()))

        if req_type == "expandNode":
            data = msg["data"]

            graph = GamebookGraph.from_graph_dict(data["graph"])
            node_to_expand = data["nodeToExpand"]

            generator.expand_graph_once(graph, node_to_expand)
            # example serialization
            self.write(json.dumps({"graph": graph.to_graph_dict()}))

            # TODO: need to generate and send back a graph with expanded node - using text_generator
        elif req_type == "endNode":
            data = msg["data"]

            graph = GamebookGraph.from_graph_dict(data["graph"])
            node_to_end = data["nodeToEnd"]

            # Ends current graph path
            generator.expand_graph_once(graph, node_to_end, True)
            
            self.write(json.dumps({"graph": graph.to_graph_dict()}))

        elif req_type == "connectNode":
            data = msg["data"]
            graph = GamebookGraph.from_graph_dict(data["graph"])
            from_node = data["fromNode"]
            to_node = data["toNode"]
            
            generator.bridge_node(graph, from_node, to_node)
            self.write(json.dumps({"graph": graph.to_graph_dict()}))
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
