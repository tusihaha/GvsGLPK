import time
from Graph.graph import Graph

def timetable(e1, e2, filename):
    """
    Description: Course timetable
    """
    start_time = time.time()

    g = Graph(e1, e2)
    g.select(0)
    g.select(1)
    g.make_regular()
    g.edges_color()
    g.info(filename)

    f = open(filename, 'a')
    f.write('\nExecuted time: ' + str(time.time() - start_time))
    f.close()
    
    return len(g.matching)