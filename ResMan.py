#!/usr/bin/python
import sys
import matplotlib.pyplot as plt
import networkx as nx
import warnings
warnings.filterwarnings("ignore",".*GUI is implemented.*")


PAUSE_VAL = 1

class ResMan:
    """
    Resource manager
    """

    def __init__(self):
        """
        initialize variables
        """
        self.fileName = ""          # name of file parameter
        self.contents = []          # contents of file
        self.processes = 0          # num of processes
        self.resources = 0          # num of resources
        self.resourceList = []      # list of resources
        self.usedResources = []     # list of resources in use
        self.processDict = {}       # dictionary of processes and the resources they own
        self.waitingList = []       # list of tuples of processes waiting on a res
        self.lockedProcesses = []   # list of locked processes
        self.deadlocked = False     # is the system deadlocked?
        self.G = nx.DiGraph()       # the graph

        # ensuring arguments entered
        if len(sys.argv) > 1:
            self.fileName = sys.argv[1]

        else:
            print("Please enter a data file argument.")
            exit(1)

    def readFile(self):
        """
        Reads contents of the input file and
        instantiates class variables
        """
        file = open(self.fileName, "r")
        self.contents = file.read().split('\n')

        self.processes = int(self.contents[0][0])
        self.resources = int(self.contents[1][0])

        # clean up to allow for easier reading of remaining values
        self.contents.pop(0)
        self.contents.pop(0)

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
        Draws the current state & checks for deadlock
        """
        # clears old data before drawing again
        plt.clf()
        plt.axis('off')

        # get list of processes and resources
        processes = self.processDict.keys()

        # get edges (list of tuples)
        edges = []      # Owned resources
        for key in self.processDict:
            for value in self.processDict[key]:
                edges.append((value,key))

        # print(processes)
        # print("edges: ", edges)
        # print("waitingList: ", self.waitingList)

        # Read nodes/edges into networkx and draw
        self.G.add_nodes_from(processes + self.resourceList)
        self.G.add_edges_from(edges+self.waitingList)
        pos = nx.bipartite_layout(self.G, nodes=processes,align='horizontal')
        nx.draw_networkx(self.G, pos, nodelist=self.resourceList,
                            node_color='y',node_size=600,with_labels=True,
                            label="Resources",edgelist=edges,edge_color='g',
                            alpha=1)
        nx.draw_networkx(self.G, pos, nodelist=processes,
                            node_color='r',node_size=600,with_labels=True,
                            label="Processes",edgelist=self.waitingList,edge_color='b',
                            alpha=1)

        # Check for deadlock!
        # get list of cycles from networkx graph
        cycles = list(nx.simple_cycles(self.G))
        # print("cycles: ",cycles)
        # print("processes: ", self.processDict.keys())

        for cycleList in cycles:
            # get nodes from cycle list
            if len(cycleList) > 2:
                for node in cycleList:
                    if node in self.processDict.keys() and node not in self.lockedProcesses:
                        self.lockedProcesses.append(node)
        # check for system deadlock
        if len(self.lockedProcesses) == self.processes:
            self.deadlocked = True
            return
        # else list locked processes
        elif len(self.lockedProcesses) > 0:
            print("Locked Processes: ", self.lockedProcesses)

        plt.waitforbuttonpress()

    def step(self):
        """
        gets next step

        idea: make this its own class to save each
        step as an object to refer back to?
        """
        thisStep = self.contents[0].split(' ')
        self.contents.pop(0)
        print(thisStep)

        proc = thisStep[0]  # current process
        cmd = thisStep[1]   # current command
        res = thisStep[2]   # current resource

        # if the process is locked, it can't do anything
        if proc not in self.lockedProcesses:
            # handle requests
            if cmd == "requests":

                # make sure resource is not already held
                if res in self.usedResources:
                    self.waitingList.append((proc, res))

                else:
                    self.processDict[proc].append(res)
                    self.usedResources.append(res)
                    print(proc+ " now owns "+ res)
            # handle releases
            elif cmd == "releases":
                # Assume if trying to release, the process has control already
                self.G.remove_edge(res,proc)
                self.processDict[proc].remove(res)
                self.usedResources.remove(res)
                print(proc + " released " + res)

                # search waiting list for that resource
                for tuple in self.waitingList:
                    if res in tuple:
                        self.draw()
                        self.processDict[tuple[0]].append(res)
                        self.usedResources.append(res)
                        self.waitingList.remove(tuple)
                        break

            self.draw()

    def main(self):
        self.readFile()
        self.draw()
        plt.axis('off')
        plt.ion()
        # plt.legend()      looks weird  TODO: fix if I have time
        plt.show()

        # loop to run the manager
        for i in range(0,len(self.contents)-1):
            if self.deadlocked:
                print("Deadlocked.  Cannot continue.")
                self.deadlocked = False
                break
            else:
                self.step()

        if self.deadlocked:
            print("Deadlocked. Cannot continue.")
        raw_input("Press enter to quit..")


main = ResMan()
main.main()
