
import requests
import json
from sklearn.naive_bayes import GaussianNB
import numpy




class EEG_Analyzer(object):

    def __init__(self):
        numpy.seterr(divide='ignore')
        numpy.seterr(invalid='warn')
        self.curr_thetas = []
        self.curr_betas = []
        self.curr_alphas = []
        self.curr_gammas = []
        self.curr_deltas = []

        self.processed_data = dict()

        self.curr_heart_rates = []

        self.classifications = ['relaxed','focused','hyped']
        self.array_size = 100

    def round_to(self,n, precision):
        correction = 0.5 if n >= 0 else -0.5
        return int( n/precision+correction ) * precision


    def train_model(self):

        all_samples = []
        all_solutions = []

        # ----- query for some datum ----- #
        for index, val in enumerate(self.classifications):

            # ---- make request to Caleb ---- #
            response = requests.get("https://hackpoly-mu.herokuapp.com/classification/"+val)

            parsed = json.loads(response.text)

            alpha = parsed.get('alpha')
            beta  = parsed.get('beta')
            delta = parsed.get('delta')
            gamma = parsed.get('gamma')
            theta = parsed.get('theta')

            # heart_rate = [parsed.get('heart_rate')] * len(theta)

            samples = list(zip(alpha,beta,delta,gamma,theta))
            # [(...),(...)....]

            solutions = [index] * len(samples)

            #samples = [sample.append(heart_rate) for sample in samples]

            # ------- aggregate ------ #
            all_samples += samples
            all_solutions += solutions

            self.trained_model = self.train_model.fit(all_samples,all_solutions)

    def shorten_array(self, arr_to_shorten):

        array_to_return = [0] * 100
        #(arr_to_shorten)
        length = len(arr_to_shorten)
        if length < 100:
            length = 100

        for i, val in enumerate(arr_to_shorten):
            array_to_return[i % 100] += val / int(length/100)

        return array_to_return





    def parse_input(self, current_vals):
        # --- currently just averages:

        current_vals = list(filter(lambda x: x != -1, current_vals))

        #print(current_vals)

        if len(current_vals) == 0:
            return 0

        val = sum(current_vals) / len(current_vals)

        rounded_val = self.round_to(val,0.05)

        print(round(rounded_val,2))
        return round(rounded_val,2)

    def analyze_brainwaves(self,song_name):


        all_samples = []
        all_solutions = []

        # ----- query for some datum ----- #
        for index, val in enumerate(self.classifications):

            # ---- make request to Caleb ---- #
            response = requests.get("https://hackpoly-mu.herokuapp.com/classification/"+val)

            parsed = json.loads(response.text)

            alpha = parsed.get('alpha')
            beta  = parsed.get('beta')
            delta = parsed.get('delta')
            gamma = parsed.get('gamma')
            theta = parsed.get('theta')

            # heart_rate = [parsed.get('heart_rate')] * len(theta)

            samples = list(zip(alpha,beta,delta,gamma,theta))
            # [(...),(...)....]

            solutions = [index] * len(samples)

            #samples = [sample.append(heart_rate) for sample in samples]

            # ------- aggregate ------ #
            all_samples += samples
            all_solutions += solutions

        # ------- train the model ---- #
        # all_samples is fully stocked
        # all_solution is fully stocked

        gaussian_model = GaussianNB()

        #print(train_data)

        #solution_wrapper = numpy.array(solutions)
        #heart_rate = 0
        #if len(self.curr_heart_rates) == 0:
        #    heart_rate = 70
        #else:
        #    heart_rate = sum(self.curr_heart_rates) / len(self.curr_heart_rates)

        #heart_rates = [heart_rate] * len(self.curr_thetas)

        test_samples = list(zip(self.curr_alphas,self.curr_betas,self.curr_deltas,self.curr_gammas,self.curr_thetas))
        # [(...),(...)]
        #test_samples = [samp.append(self.curr_heart_rates[i]) for i, samp in enumerate(self.curr_heart_rates)]

        predictions = self.train_model.predict(test_samples)

        print("Predictions: ",end="")
        print(predictions[:50])

        outcome = max(predictions,key = predictions.tolist().count)
        print("Outcome: ",end="")
        print(outcome)

        score = predictions.tolist().count(outcome)/len(predictions)
        print("Score: ",end="")
        print(score)

        # ----- send data to Caleb ---- #

        url = "https://hackpoly-mu.herokuapp.com/user"

        data = {
            'classification': outcome.item(),
            'song-id': song_name,
            'song-rating': score,
        }
        requests.post(url,json=data)

        self.processed_data = data



            # 'alpha' : [ .... ] : len = 100
            # 'beta' : [ .... ] : len = 100
            # 'delta' : [ .... ] : len = 100
