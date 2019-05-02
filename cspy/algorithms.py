#!/usr/bin/env pypy

# import networkx as nx
from .label import Label
from collections import OrderedDict


class expand:
    pass


class BiDirectional:
    ''' bidirectional labeling algorithm with dynamic half-way point.
    PARAMS
        G :: Digraph;
        L :: float, lower bound for resource usage;
        U :: float, upper bound for resource usage;'''

    def __init__(self, G, L, U):
        self.G, self.n_edges = G, len(G.edges())
        self.HB = L
        self.HF = U
        self.F, self.B = expand(), expand()
        self.F.Label = Label(
            0, 'Source', [0] * G.graph['n_res'], ['Source'])
        self.B.Label = Label(
            0, 'Sink', [self.n_edges + 1] * G.graph['n_res'], ['Sink'])
        self.F.unprocessed, self.B.unprocessed = {}, {}
        self.finalFpath, self.finalBpath = [], []

    def run(self):
        while self.F.Label or self.B.Label:
            direction = self.getDirection()
            if direction == 'forward':  # forward
                if self.F.Label.res[0] <= self.HF:
                    if self.F.Label not in self.F.unprocessed.keys():
                        self.F.unprocessed[self.F.Label] = {}
                    edges = [e for e in self.G.edges(data=True)
                             if e[0] == self.F.Label.node]
                    # edges = [(i, j) for j in self.G.successors_iter(i)]
                    list(map(self.progateFlabel, edges))
                    self.HB = max(self.HB, min(self.F.Label.res[0], self.HF))
                    self.getNextFlabel()
                    if self.F.Label and self.F.Label.node == 'Sink':
                        break
            elif direction == 'backward':
                if self.B.Label.res[0] > self.HB:
                    if self.B.Label not in self.B.unprocessed.keys():
                        self.B.unprocessed[self.B.Label] = {}
                    edges = [e for e in self.G.edges(data=True)
                             if e[1] == self.B.Label.node]
                    list(map(self.progateBlabel, edges))
                    self.HF = min(self.HF, max(self.B.Label.res[0], self.HB))
                    self.getNextBlabel()
                    if self.B.Label and self.B.Label.node == 'Source':
                        break
            else:
                break
            self.checkDominance()
        return self.joinPaths()

    def getDirection(self):
        import random

        if self.F.Label and not self.B.Label:
            return 'forward'
        elif not self.F.Label and self.B.Label:
            return 'backward'
        elif self.F.Label and self.B.Label:
            # return 'forward'
            return random.choice(['forward', 'backward'])
        else:  # if both are empty
            return

    def progateFlabel(self, edge):
        weight, res_cost = edge[2]['weight'], edge[2]['res_cost']
        new_label = self.F.Label.getNewLabel(
            'forward', weight, edge[1], res_cost)
        if new_label.res[0] <= self.HF:  # feasibility check
            self.F.unprocessed[self.F.Label][new_label] = new_label.path

    def progateBlabel(self, edge):
        weight, res_cost = edge[2]['weight'], edge[2]['res_cost']
        new_label = self.B.Label.getNewLabel(
            'backward', weight, edge[0], res_cost)
        if new_label.res[0] > self.HB:  # feasibility check
            self.B.unprocessed[self.B.Label][new_label] = new_label.path

    def getNextFlabel(self):
        # Update next forward label with one with least weight
        if self.F.Label in self.F.unprocessed.keys():
            labels_dict = self.F.unprocessed[self.F.Label]
            if labels_dict:
                del self.F.unprocessed[self.F.Label]
                self.F.Label = min(labels_dict.keys(),
                                   key=lambda x: x.weight)
                self.finalFpath = self.F.Label.path

            else:
                self.finalFpath = self.F.Label.path
                self.F.Label = None

    def getNextBlabel(self):
        if self.B.Label in self.B.unprocessed.keys():
            labels_dict = self.B.unprocessed[self.B.Label]
            if labels_dict:
                del self.B.unprocessed[self.B.Label]
                self.B.Label = min(labels_dict.keys(),
                                   key=lambda x: x.weight)
                self.finalBpath = self.B.Label.path
            else:
                self.finalBpath = self.B.Label.path
                self.B.Label = None

    def checkDominance(self):
        # print(self.F.unprocessed)
        # print(self.B.unprocessed)

        for label_dicts in self.B.unprocessed.values():
            if len(label_dicts) >= 1:
                print(sorted(label_dicts.keys()))
        # for labels in self.F.unprocessed.values():
        #     labels_sorted = labels
        # if a[0] == b[0] and all(a[1] == b[1]):
        #     label_dominated = False
        # else:
        #     label_dominated = True
        #     if a[0] < b[0]:
        #         label_dominated = False
        #     if any(a[1] < b[1]):
        #         label_dominated = False
        # for label in self.F.unprocessed[self.F.Label].keys():
        pass

    def joinPaths(self):
        print(self.finalBpath)
        print(self.finalFpath)
        self.finalBpath.reverse()  # reverse order for backward path
        print(list(OrderedDict.fromkeys(self.finalFpath + self.finalBpath)))
        return list(OrderedDict.fromkeys(self.finalFpath + self.finalBpath))
