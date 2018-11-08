#!/usr/bin/python
import sys
import matplotlib.pyplot as plt
import networkx as nx


class ResMan:
    """
    Resource manager
    """

    def __init__(self):
        """
        initialize variables
        """
        self.fileName = ""
        self.contents = []
        self.processes = 0
        self.resources = 0
        self.resourceList = []
        self.usedResources = []
        self.processDict = {}
        self.waitingList = []
        self.G = nx.DiGraph()
        # ensuring arguments entered
        if len(sys.argv) > 1:
            self.fileName = sys.argv[1]

        else:
            print("Please enter a data file argument.")
            exit(1)
        # readFile(self, fileName)

    def readFile(self):
        """
        Reads contents of the input file and
        instantiates class variables
        """
        file = open(self.fileName, "r")
        self.contents = file.read().split('\r\n')

        self.processes = int(self.contents[0][0])
        self.resources = int(self.contents[1][0])

        # clean up to allow for easier reading of remaining values
        self.contents.pop(0)
        self.contents.pop(0)
        # print(self.contents)

        # create list of resources for graphing purposes
        for i in range(0, self.resources):
            resName = 'r'+str(i)
            self.resourceList.append(resName)
        self.resourceList.sort()

        # create dictionary of processes
        for i in range(0, self.processes):
            procName = 'p'+str(i)
            self.processDict[procName] = []

    def draw(self):
        """
        Draws the current state
        """
        # G = nx.DiGraph()
        # get list of processes and resources
        processes = self.processDict.keys()

        # get edges (list of tuples)
        edges = []
        for key in self.processDict:
            for value in self.processDict[key]:
                edges.append((value,key))

        # print(processes)
        print("edges: ", edges)
        print("waitingList: ", self.waitingList)

        self.G.add_nodes_from(processes + self.resourceList)
        # self.G.add_edges_from(edges, color='g')
        self.G.add_edges_from(edges+self.waitingList)
        # Read nodes into networkx
        pos = nx.bipartite_layout(self.G, nodes=processes,align='horizontal')
        nx.draw_networkx(self.G, pos, nodelist=self.resourceList,
                            node_color='y',node_size=600,with_labels=True,
                            label="Resources",edgelist=edges,edge_color='g',
                            alpha=1)
        nx.draw_networkx(self.G, pos, nodelist=processes,
                            node_color='r',node_size=600,with_labels=True,
                            label="Processes",edgelist=self.waitingList,edge_color='b',
                            alpha=1)

    def step(self):
        """
        gets next step

        idea: make this its own class to save each
        step as an object to refer back to?
        """
        thisStep = self.contents[0].split(' ')
        self.contents.pop(0)
        print(thisStep)

        proc = thisStep[0]
        cmd = thisStep[1]
        res = thisStep[2]

        # print("Nodes in G: ", self.G.nodes(data=True))
        print("Edges in G: ", self.G.edges(data=True))
        # make sure resource is not already held
        if cmd == "requests":
            # handle requests
            for list in self.processDict.values():

                if res in list:
                    self.waitingList.append((proc, res))
                    self.draw()
                    return

            self.processDict[proc].append(res)
        elif cmd == "releases":
            # Assume if trying to release, the process has control already
            self.G.remove_edge(res,proc)
            self.processDict[proc].remove(res)
            # search waiting list for that resource

        print(self.processDict)
        self.draw()

    def main(self):
        self.readFile()
        self.draw()
        plt.axis('off')
        plt.ion()
        # plt.legend()      looks weird  TODO: fix if I have time
        plt.show()
        for i in range(0,len(self.contents)-1):
            plt.clf()
            plt.axis('off')
            self.step()
            plt.pause(1)

        raw_input("Press enter to quit..")


main = ResMan()
main.main()
