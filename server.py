from tree import GamebookTree, GamebookNodeData

import tornado
import tornado.websocket
import json

LISTEN_PORT = 8000
LISTEN_ADDRESS = '127.0.0.1'

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    """Simple WebSocket handler to serve clients."""

    @classmethod
    def urls(cls):
        return [
            (r'/ws/(.*)', cls, {}),
        ]

    def open(self, channel):
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

        if req_type == "expand_node":
            data = msg["data"]

            adjacency_lists = data["graph"]["adjacency_lists"]
            node_data_list = [GamebookNodeData(node["action"], node["consequence"]) for node_data in data["graph"]["nodes"]]
            node_to_expand = data["node_to_expand"]

            graph = GamebookTree(adjacency_lists, node_data_list)

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
    http_server.listen(LISTEN_PORT, LISTEN_ADDRESS)
    
    # Start IO/Event loop
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    # TODO: construct a text generator with a model
    main()
