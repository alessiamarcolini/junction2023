import socketio

sio = socketio.SimpleClient()
sio.connect("http://localhost:5000")

sio.emit("execute", {"messages": ["Hello", "World"]})

while True:
    event = sio.receive()
    print(event)
