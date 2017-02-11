# Author: Samuel Resendez



import tornado.ioloop
import tornado.web
import tornado.websocket


muse_sockets = []

class eeg_socket(tornado.websocket.WebSocketHandler):

    def check_origin(self,origin):
        return True


    def open(self):
        if self not in muse_sockets:
            muse_sockets.append(self)

    def on_close(self):
        if self in muse_sockets:
            muse_sockets.remove(self)

    def on_message(self,message):
        # --- handle logic to parse message ------ #

        print(message)


        # --- send to Caleb --- #
        for connection in muse_sockets:
            connection.write_message(message)



class music_handler(tornado.web.RequestHandler):

    def post(self,data):
        print(data)

    def get(self):
        self.write("""
        <h1> Song endpoint </h1>
        <p> Make a POST request with the following param format:
        { 'song_name': the song name }
        </p>



        """)



# ------- execution begins ------- #

app = tornado.web.Application([
    (r'/muse_socket',eeg_socket),
    (r'/song_name',music_handler),
])



if __name__ == "__main__":
    app.listen(8000)
    print("Server has started on port: 8000")
    tornado.ioloop.IOLoop.instance().start()
