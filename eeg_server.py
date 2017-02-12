# Author: Samuel Resendez



import tornado.ioloop
import tornado.web
import tornado.websocket
import tornado.options
import json, requests
from eeg_analyzer import EEG_Analyzer

from tornado.options import define, options, parse_command_line


define("port", default=5000, help="run on the given port", type=int)

muse_sockets = []
database_sockets = []
listeners = []
processed_clients = []



# I got this #

# FIGHT ON #

# --- machine learning / data interface --- #
analyzer = EEG_Analyzer()


class eeg_socket(tornado.websocket.WebSocketHandler):

    def check_origin(self,origin):
        return True


    def open(self):
        print("Server is Open")
        if self not in muse_sockets:
            muse_sockets.append(self)

    def on_close(self):
        if self in muse_sockets:
            muse_sockets.remove(self)

    def on_message(self,message):
        # --- handle logic to parse message ------ #
        parsed_json = json.loads(message)
        #print(parsed_json)

        # --- setting up config stuff --- #

        curr_class = "relaxed"
        caleb_url = "https://hackpoly-mu.herokuapp.com/classification"
        is_training = False

        # -^- Only use while training -^- #

        if 'delta_relative' in parsed_json:
            deltas = parsed_json.get('delta_relative')
            processed = analyzer.parse_input(deltas)
            if processed > 0:
                analyzer.curr_deltas.append(processed)

                obj = {
                'delta':processed,
                }
                for lis in listeners:
                    lis.write_message(obj)

        elif 'alpha_relative' in parsed_json:
            alphas = parsed_json.get('alpha_relative')
            processed = analyzer.parse_input(alphas)
            if processed > 0:
                analyzer.curr_alphas.append(processed)

                obj = {
                'alpha':processed,
                }

                for lis in listeners:
                    lis.write_message(obj)

        elif 'gamma_relative' in parsed_json:
            gammas = parsed_json.get('gamma_relative')
            processed = analyzer.parse_input(gammas)
            if processed > 0:
                analyzer.curr_gammas.append(processed)

                obj = {
                'gamma':processed,
                }

                for lis in listeners:
                    lis.write_message(obj)

        elif 'beta_relative' in parsed_json:
            betas = parsed_json.get('beta_relative')
            processed = analyzer.parse_input(betas)
            if processed > 0:
                analyzer.curr_betas.append(processed)

                obj = {
                'beta':processed,
                }

                for lis in listeners:
                    lis.write_message(obj)

        elif 'theta_relative' in parsed_json:
            thetas = parsed_json.get('theta_relative')
            processed = analyzer.parse_input(thetas)
            if processed != 0:
                analyzer.curr_thetas.append(processed)

                obj = {
                'theta':processed,
                }

                for lis in listeners:
                    lis.write_message(obj)

        elif 'heart_rate' in parsed_json:
            rate = parsed_json.get('heart_rate')
            processed = analyzer.parse_input(rate)

            if processed != 0:
                analyzer.curr_heart_rates.append(processed)

                obj = {
                'heart_rate':processed,
                }

                for lis in listeners:
                    lis.write_message(obj)

        # --- FOR TRAINING ONLY --- #
        if is_training and len(analyzer.curr_thetas) >= 100 and len(analyzer.curr_betas) >= 100 and len(analyzer.curr_alphas) >= 100 and len(analyzer.curr_deltas) >= 100 and len(analyzer.curr_gammas) >= 100 and len(analyzer.curr_heart_rates):
            # --- send first 100 to Caleb --- #
            avg_heart_rate = 0
            if len(analyzer.curr_heart_rates) == 0:
                avg_heart_rate = 90
            else:
                avg_heart_rate = sum(analyzer.curr_heart_rates) / len(analyzer.curr_heart_rates)
            packet = {
                'class': curr_class,
                'heart_rate': analyzer.curr_heart_rates[:100],
                'alpha': analyzer.curr_alphas[:100],
                'beta': analyzer.curr_betas[:100],
                'delta':analyzer.curr_deltas[:100],
                'gamma':analyzer.curr_gammas[:100],
                'theta':analyzer.curr_thetas[:100],
            }
            requests.post(caleb_url, json = packet)
            print("Sent data to caleb")

            analyzer.curr_thetas = []; analyzer.curr_betas = []; analyzer.curr_alphas = []; analyzer.curr_deltas = []; analyzer.curr_gammas = []
            analyzer.curr_heart_rates = []

class music_handler(tornado.websocket.WebSocketHandler):


    def check_origin(self,origin):
        return True

    def on_message(self,message):
        print(message)
        parse = json.loads(message)
        analyzer.analyze_brainwaves(parse['track_id'])
        #analyzer.analyze_brainwaves("1234")

        for cl in processed_clients:
            cl.write_message(analyzer.processed_data)

class eeg_data_socket(tornado.websocket.WebSocketHandler):

    def check_origin(self,origin):
        return True

    def open(self):
        if self not in listeners:
            listeners.append(self)

    def on_close(self):
        if self in listeners:
            listeners.remove(self)

class processed_eeg_data_socket(tornado.websocket.WebSocketHandler):

    def check_origin(self,origin):
        return True

    def open(self):
        if self not in processed_clients:
            processed_clients.append(self)

    def on_close(self):
        if self in processed_clients:
            processed_clients.remove(self)

def hi():
    for cl in muse_sockets:
        cl.write_message('hi')
    for cl in database_sockets:
        cl.write_message('hi')
    for cl in listeners:
        cl.write_message('hi')
    for cl in processed_clients:
        cl.write_message('hi')

# ------- execution begins ------- #

app = tornado.web.Application([
    (r'/muse_socket',eeg_socket),
    (r'/song_name',music_handler),
    (r'/raw_data',eeg_data_socket),
    (r'/parsed_data',processed_eeg_data_socket)
])



if __name__ == "__main__":
    parse_command_line()
    app.listen(options.port)

    tornado.ioloop.PeriodicCallback(hi, 2000).start()

    tornado.ioloop.IOLoop.instance().start()
