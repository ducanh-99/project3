from hashlib import new
import random
import bisect
import csv
import datetime
import time


class StartDate:
    year = 2020
    month = 1
    date = 1


class EndDate:
    year = 2021
    month = 1
    date = 1


class graph:
    def __init__(self, gdict=None, res=[]):
        if gdict is None:
            gdict = {}
        self.gdict = gdict
        self.res = res

    def getVertices(self):
        return list(self.gdict.keys())

    def addVertex(self, v):
        if v not in self.gdict:
            self.gdict[v] = {}

    def addEdge(self, v1, v2, w):
        if v1 in self.gdict:
            self.gdict[v1][v2] = w
        else:
            self.gdict[v1] = [[v2, w]]

    def printGraph(self):
        for vertex in self.gdict:
            for edge in self.gdict[vertex]:
                print(str(vertex) + " -> " + str(edge) +
                      ", edge weight: " + str(self.gdict[vertex][edge]))

    def getSubGraph(self, vertexSet):
        res = graph(None)
        for v1 in vertexSet:
            #print("First vertex is :", v1)
            res.addVertex(v1)
            for v2 in vertexSet:
                #print("Second vertex is :", v2)

                if v2 in self.gdict[v1]:
                    #print(v1, " --> ", v2)
                    res.addEdge(v1, v2, self.gdict[v1][v2])

                #print ("-----")
        return res

    def getRandomWeightedVertex(self, v):
        sums = {}
        S = 0
        for vertex in self.gdict[v]:
            if vertex not in self.res:
                # print "Adding " + str(self.gdict[v][vertex])
                S += self.gdict[v][vertex]
                sums[vertex] = S

        # print sums
        r = random.uniform(0, S)
        for k in sums.keys():
            if (r <= sums[k]):
                return k

    def randomWeightedPath(self, first_edge, max_len):
        self.res = []
        prev_vertex = 0
        self.res.append(first_edge)
        weight_value = 0
        while(len(self.res) < len(self.gdict.keys())):
            new_vertex = self.getRandomWeightedVertex(prev_vertex)
            if len(self.res) >= max_len:
                break
            if new_vertex not in self.res:
                self.res.append(new_vertex)
                weight_value += self.gdict[prev_vertex][new_vertex]
                prev_vertex = new_vertex

            else:
                continue
        return self.res, weight_value

    def generateTime(self, duration):
        rtime = int(random.random()*86400)

        hours = 0
        while hours < 7 or (12 < hours and hours < 12) or 17 < hours:
            rtime = int(random.random()*86400)
            hours = int(rtime/3600)

        minutes = int((rtime - hours*3600)/60)
        seconds = rtime - hours*3600 - minutes*60

        time_string = datetime.time(hour=hours, minute=minutes, second=seconds)

        return time_string

    def generateDate(self):
        start_date = datetime.date(
            StartDate.year, StartDate.month, StartDate.date)
        end_date = datetime.date(EndDate.year, EndDate.month, EndDate.date)

        time_between_dates = end_date - start_date
        days_between_dates = time_between_dates.days
        random_number_of_days = random.randrange(days_between_dates)
        random_date = start_date + \
            datetime.timedelta(days=random_number_of_days)

        print(random_date)

    def autoPlus(self, duration, start_time):
        minutes_added = datetime.timedelta(minutes=duration)
        end_time = start_time + minutes_added
        print(end_time)
        return end_time


testgraph = graph({0: {1: 5, 2: 0, 3: 5, 4: 0, 5: 1, 6: 1, 7: 4, 8: 2, 9: 0, 10: 12},
                   1: {0: 0, 2: 2, 3: 8, 4: 0, 5: 1, 6: 1, 7: 15, 8: 0, 9: 4, 10: 1},
                   2: {0: 0, 1: 5, 3: 5, 4: 0, 5: 0, 6: 4, 7: 3, 8: 2, 9: 1, 10: 1},
                   3: {0: 0, 1: 4, 2: 6, 4: 0, 5: 1, 6: 3, 7: 2, 8: 0, 9: 1, 10: 6},
                   4: {0: 3, 1: 4, 2: 3, 5: 2, 6: 0, 7: 0, 8: 0, 9: 0, 10: 0},
                   5: {0: 2, 1: 4, 2: 10, 4: 0,  6: 0, 7: 0, 8: 0, 9: 0, 10: 0},
                   6: {0: 2, 1: 4, 2: 10, 4: 0, 5: 0, 7: 1, 8: 0, 9: 1, 10: 0},
                   7: {0: 2, 1: 4, 2: 10, 4: 0, 5: 0, 6: 0,  8: 0, 9: 1, 10: 0},
                   8: {0: 2, 1: 4, 2: 10, 4: 0, 5: 0, 6: 10, 7: 0,  9: 1, 10: 2},
                   9: {0: 2, 1: 4, 2: 10, 4: 0, 5: 0, 6: 3, 7: 4, 8: 0,  10: 2},
                   10: {0: 2, 1: 4, 2: 10, 4: 0, 5: 0, 6: 2, 7: 8, 8: 5, 9: 3}
                   })
res = []
for i in range(5):
    max_len = random.randrange(1, 10)
    first_edge = random.randrange(0, 9)
    # print(testgraph.randomWeightedPath(first_edge, max_len))
    a = testgraph.generateTime(5)
    # testgraph.generateDate()
    testgraph.autoPlus(start_time=a, duration=4)
    # res.append(testgraph.randomWeightedPath(
    #     first_edge=first_edge, max_len=max_len)[0])

# f = open('data.csv', 'a')

# with f:

#     writer = csv.writer(f)

#     for row in res:
#         writer.writerow(row)
