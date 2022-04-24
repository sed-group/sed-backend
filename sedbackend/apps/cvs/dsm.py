from sedbackend.apps.cvs import models
from typing import List

def createDSM(bpmn: models.BPMNGet):
    nodes: List[models.NodeGet]
    edges: List[models.EdgeGet]
    nodes = bpmn.nodes
    edges = bpmn.edges
    dsm = emptyDSM(len(nodes))

    populateDSM(dsm, nodes, edges)

    return dsm

def emptyDSM(length):
    matrix = [0] * length
    for i in range(len(matrix)):
        matrix[i] = [0] * length
    return matrix

def populateDSM(DSM, nodes: List[models.NodeGet], edges: List[models.EdgeGet]):
    for e in edges:
        DSMfrom = nodes.index(e.from_node)
        DSMto = nodes.index(e.to_node)
        DSM[DSMfrom][DSMto] = e.probability