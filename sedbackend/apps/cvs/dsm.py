import numpy as np

def createDSM(BPMN):
    nodes = BPMN.getNodes
    edges = BPMN.getEdges
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
        DSMfrom = nodes.index(e.fromNode)
        DSMto = nodes.index(e.toNode)
        DSM[DSMfrom][DSMto] = 1