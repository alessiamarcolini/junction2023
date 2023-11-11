import sys

import socketio
from model_handler.socket_model_handler import SocketModelHandler

module_name = sys.argv[1]
module_import = __import__(module_name, fromlist=["Orchestrator"])

print("Loading orchestrator")
orchestrator = module_import.Orchestrator()

print("Starting app in socket mode")
sio = socketio.Client()


@sio.event
def execute(data):
    print(f"execution requested {data}")
    handler = SocketModelHandler(data, sio)
    orchestrator.execute(handler)


@sio.event
def connect():
    print("Connected to executor service")

@sio.on("*")
def handle_messages(event, *args):
    print(f"Recieved message {event} {args}")

@sio.event
def disconnect():
    print("Disconnected from executor service")


sio.connect("http://localhost:5001")
sio.wait()
