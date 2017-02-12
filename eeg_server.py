# Author: Samuel Resendez



import tornado.ioloop
import tornado.web
import tornado.websocket
import json, requests
from eeg_analyzer import EEG_Analyzer


muse_sockets = []
database_sockets = []


current_song = ""

# ---- stores aggregate data ------- #
curr_thetas = []
curr_betas = []
curr_alphas = []
curr_gammas = []
curr_deltas = []
# ---- tbh, this is boutta be hella scary ----- #


class eeg_socket(tornado.websocket.WebSocketHandler):

    def check_origin(self,origin):
        return True


    def open(self):
        print(current_song)
        if self not in muse_sockets:
            muse_sockets.append(self)

    def on_close(self):
        if self in muse_sockets:
            muse_sockets.remove(self)

    def on_message(self,message):
        # --- handle logic to parse message ------ #
        parsed_json = json.loads(message)

        if 'delta_relative' in parsed_json:
            deltas = parsed_json.get('delta_relative')
            curr_deltas.append(EEG_Analyzer().parse_input(deltas))
            print(deltas)

        elif 'alpha_relative' in parsed_json:
            alphas = parsed_json.get('alpha_relative')
            curr_alphas.append(EEG_Analyzer().parse_input(alphas))
            print(alphas)

        elif 'gamma_relative' in parsed_json:
            gammas = parsed_json.get('gamma_relative')
            curr_gammas.append(EEG_Analyzer().parse_input(gammas))
            print(gammas)

        elif 'beta_relative' in parsed_json:
            betas = parsed_json.get('beta_relative')
            curr_betas.append(EEG_Analyzer().parse_input(betas))
            print(betas)

        elif 'theta_relative' in parsed_json:
            thetas = parsed_json.get('theta_relative')
            curr_thetas.append(EEG_Analyzer().parse_input(thetas))
            print(thetas)



        print(message)


        # --- send to Caleb --- #
        for connection in muse_sockets:
            connection.write_message(message)



class music_handler(tornado.web.RequestHandler):

    def post(self):
        song_name = self.get_argument('song_name',"No data")
        if song_name != "No data":
            print(song_name)
            classification = EEG_Analyzer().analyze_brainwaves(curr_alphas,curr_betas,curr_deltas,curr_gammas,curr_thetas)

            # -- send classification and song name to Caleb -- #
            requests.post("https://hackpoly-mu.herokuapp.com/",data={'song_name':song_name,'classification':classification})



    def get(self):
        self.write("""
        <h1> Song endpoint </h1>
        <p> Make a POST request with the following param format:
        { 'song_name': the song name }
        </p>
        """)


class database_handler(tornado.websocket.WebSocketHandler):

    def open(self):
        print("connection established with database")

        if self not in database_sockets:
            database_sockets.append(self)


    def on_close(self):
        if self in database_sockets:
            database_sockets.remove(self)






# ------- execution begins ------- #

app = tornado.web.Application([
    (r'/muse_socket',eeg_socket),
    (r'/song_name',music_handler),
])



if __name__ == "__main__":
    app.listen(8000)
    print("Server has started on port: 8000")
    tornado.ioloop.IOLoop.instance().start()
