import math
import pandas as pd
import os
import ast

class Recommender():
    def __init__(self, museums_bin="museums_binary.csv", museums="raw_dataset.xlsx"):
        dir_path = os.getcwd()
        self.museums_bin = pd.read_csv(dir_path + "/datasets/" + museums_bin)
        self.museums = pd.read_excel(dir_path + "/datasets/" + museums)

    def _cosine(self, point1, point2):
            w = 0
            x = 0
            y = 0
            z = 0
            for i in range(len(point1)):
                x += (point1[i] * point2[i])
                y += math.pow(point1[i], 2)
                z += math.pow(point2[i], 2)
            w = (math.sqrt(y) * math.sqrt(z))
            return 1 - (x / w) if w != 0 else 0

    def _cosine_distance(self, museum_id_1, museum_id_2):
        """
        Search similarity with cosine distance
        """
        a = self.museums_bin.iloc[museum_id_1]
        b = self.museums_bin.iloc[museum_id_2]
        distance = 0

        for col, val in a.iteritems():
            if col != "name":
                distance += self._cosine(ast.literal_eval(a[col]), ast.literal_eval(b[col]))

        return distance


    def knn(self, name):
        pred_museum = self.museums_bin[self.museums_bin["name"].str.contains(
            name)].iloc[0].to_frame().T

        def knn(base, K):
            distances = []

            for idx, museum in self.museums_bin.iterrows():
                if idx != base.index[0]:
                    dist = self._cosine_distance(base.index[0], idx)
                    distances.append((idx, dist))

            distances.sort(key=lambda x: x[1])
            neighbors = distances[:K]

            return neighbors

        K = 9
        neighbors = knn(pred_museum, K)
        first_museum = self.museums[self.museums["name"].str.contains(name)].iloc[0].to_frame().T
        first_museum = first_museum.to_dict(orient='records')
        first_museum[0]["id"] = 0
        recommend = first_museum

        for i, neighbor in enumerate(neighbors):
            museum = self.museums.iloc[[neighbor[0]]]
            museum = museum.to_dict(orient='records')[0]
            museum["id"] = i + 1
            recommend.append(museum)

        return recommend