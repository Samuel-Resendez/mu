

class EEG_Analyzer(object):

    def __init__(self):
        self.classifications = ['relaxed','focused','hyped']
        self.array_size = 100

    def parse_input(current_vals):

        # --- currently just averages:
        return sum(current_vals) / len(current_vals)


    def analyze_brainwaves(self, a, b, d, g, t):

        # ----- query for some datum ----- #
        


        pass
