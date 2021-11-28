import math
import pandas as pd
import os
import ast

class Recommender():
    def __init__(self, public_transport="kendaraan umum", museums_bin="museums_binary.csv", museums="raw_dataset.xlsx"):
        dir_path = os.getcwd()
        self.museums_bin = pd.read_csv(dir_path + "/datasets/" + museums_bin)
        self.museums = pd.read_excel(dir_path + "/datasets/" + museums)
        self.public_transport = public_transport

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


    def knn(self, base, exist, K):
            distances = []

            for idx, museum in self.museums_bin.iterrows():
                existed = False
                for e in exist:
                    if museum["name"] == e["name"]:
                        existed = True
                        break
                        
                if idx != base.index[0] and not existed:
                    dist = self._cosine_distance(base.index[0], idx)
                    distances.append((idx, dist))

            distances.sort(key=lambda x: x[1])
            neighbors = distances[:K]

            return neighbors


    def recommend(self, entities):
        if self.public_transport == "kendaraan pribadi":
            self.museums.drop(columns=["public_transportation", "distance_to_museum"], axis=1, inplace=True)
            self.museums_bin.drop(columns=["public_transportation_bin", "distance_bin"], axis=1, inplace=True)

        pred_museum = self.museums_bin[self.museums_bin["name"].str.contains(
            entities[0]["name"])].iloc[0].to_frame().T

        K = 10
        neighbors = self.knn(pred_museum, entities[1:], K)
        i = len(entities) + 1

        for neighbor in neighbors:
            museum = self.museums.iloc[neighbor[0]]["name"]
            museum = {
                "id": i,
                "name": museum
            }
            entities.append(museum)
            i += 1

        return entities