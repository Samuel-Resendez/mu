
from websocket import create_connection

ws = create_connection("ws://281b343a.ngrok.io/muse_socket")
#ws.connect()
ws.send("Hello there!")
