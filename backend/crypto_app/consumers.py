import os
import json
from channels.generic.websocket import WebsocketConsumer

class DashConsumer(WebsocketConsumer):
    def connect(self):
        filename = os.path.join(os.path.dirname(__file__), 'bin_json.json')
        self.accept()

        self.send(text_data=json.dumps(filename))

    def receive(self, text_data=None):
        data_json = json.loads(text_data)
        message = data_json