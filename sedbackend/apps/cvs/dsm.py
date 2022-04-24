import numpy as np

def createDSM(BPMN):
    nodes = BPMN.getNodes   # TODO Make sure the BPMN is fetched the right way
    edges = BPMN.getEdges   # TODO Make sure the BPMN is fetched the right way
    DSM = emptyDSM(len(nodes))

    populateDSM(DSM, nodes, edges)

    return DSM

def emptyDSM(length):
    matrix = [0] * length
    for i in range(len(matrix)):
        matrix[i] = [0] * length
    return matrix

def populateDSM(DSM, nodes, edges):
    for e in edges:
        DSMfrom = nodes.index(e.fromNode)   # TODO Make sure the node id fetched the right way
        DSMto = nodes.index(e.toNode)       # TODO Make sure the edge id is fetched the right way
        DSM[DSMfrom][DSMto] = 1