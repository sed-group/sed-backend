from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, LargeBinary, Boolean
from sqlalchemy.orm import relationship

import itertools #for permutations in concept DNA

Base = declarative_base()

class Tree(Base):
    """
    parent class to associate all elements of one tree to
    contains multiple concepts
    """
    __tablename__ = "tree"
    id = Column(Integer, primary_key = True)
    name = Column(String(200))
    description = Column(String(2000))
    topLvlDSid = Column(Integer, 
                    ForeignKey('designsolution.id', 
                        ondelete="SET NULL",
                        name="fk_topLvlDS"
                        ),
                    nullable=True,
                    )
    # allDS = relationship("DesignSolution", 
    #                 backref="tree",
    #                 foreign_keys="designsolution.treeID" 
    #                 )
    # allFR = relationship("FunctionalRequirement", 
    #                 backref="tree", 
    #                 )
    # allConcepts = relationship("Concept", 
    #                 backref="tree", 
    #                 )
    #### topLvlDS relationship doesn't work because pydantic crashes with circular relations!
    topLvlDS = relationship('DesignSolution', 
        uselist=False, 
        foreign_keys=[topLvlDSid])

    def __repr__(self):
        return "<Tree(name='%s')>" % (self.name)

class Concept(Base):
    """
    one instance of a tree of a tree
    """
    __tablename__ = "concept"
    id = Column(Integer, primary_key = True)
    name = Column(String(200))
    # tree link:
    treeID = Column(Integer, 
                        ForeignKey('tree.id', 
                            ondelete="CASCADE", 
                            name="fk_concept_tree")
                        )
    # tree = relationship("Tree", 
    #                 backref="concept", 
    #                 foreign_keys=[treeID])
    dna = Column(String(2000)) # List of all IDs of the DS in this concept
    def __repr__(self):
        return "<Concept(name='%s', treeID='%s', )>" % (self.name, self.treeID)
    
class DesignSolution(Base):
    """
    DS element for EF-M modelling; contains all basic information
    """
    __tablename__ = "designsolution"
    id = Column(Integer, primary_key = True)
    name = Column(String(200))
    description = Column(String(2000))
    # tree link:
    treeID = Column(Integer, 
                        ForeignKey('tree.id', 
                            ondelete="CASCADE", 
                            name="fk_ds_tree"), 
                        nullable = True)
    # tree = relationship("Tree", 
    #                     backref="designsolution", 
    #                     foreign_keys=[treeID])
    # isb: 
    isbID = Column(Integer, 
        ForeignKey('functionalrequirement.id',
                            ondelete="CASCADE", 
                            name="fk_isb_id"),
                        nullable=True)
    requires_functions = relationship("FunctionalRequirement", 
                        backref="rf", 
                        foreign_keys='[FunctionalRequirement.rfID]')
    interacts_with = relationship("InteractsWith",
                        backref="fromDS",
                        foreign_keys='[InteractsWith.fromDsID]')
    design_parameters = relationship("DesignParameter",
                        backref="ds",
                        foreign_keys='[DesignParameter.dsID]')
    # identifier if top-level-node of a tree
    #### fix because pydantic doesn't allow circular loops =()
    is_top_level_DS = Column(Boolean, default=False)

    def __repr__(self):
        return "<DS(name='%s', treeID='%s', isb_parentFRid='%s')>" % (self.name, self.treeID, self.isbID)
    
    ## function for recursive generation of alternative concepts
    def alternativeConfigurations(self):
        # creates the permutations of all child-FR alternative configurations
        # FR1 [dnaA, dnaB, dnaC]; FR2 [dna1, dna2]; FR3 [DNA]
        # --> [(dnaA, dna1, DNA), (dnaB, dna1, DNA), (dnaC, dna1, DNA),
        #      (dnaA, dna2, DNA), (dnaB, dna2, DNA), (dnaC, dna2, DNA)]
        allDNA = []
        allConfigurations = []
        for f in self.requires_functions:
            # creating a list of all DNA from each FR; one entry per FR
            # this will later be combinatorially multiplied (cross product)
            # f.linkToCC()
            allDNA.append(f.alternativeSolutions())
            # print(" allDNA of {}: {}; fr:{}, altS: {}".format(self, allDNA, f, f.alternativeSolutions()))

            # generating the combinatorial
            # the first "list" makes it put out a list instead of a map object
            # the map(list, ) makes it put out lists instead of tuples, needed for further progression on this...
            allConfigurations = list(map(list, itertools.product(*allDNA)))

        # print(allConfigurations)

        return allConfigurations
        
class FunctionalRequirement(Base):
    """
    FR element for EF-M modelling; contains all basic information
    """
    __tablename__ = "functionalrequirement"
    id = Column(Integer, primary_key = True)
    name = Column(String(200))
    description = Column(String(2000))
    # tree link:
    treeID = Column(Integer, 
                        ForeignKey('tree.id', 
                            ondelete="CASCADE", 
                            name="fk_fr_tree")
                        )
    # tree = relationship("Tree", 
    #                     backref="functionalrequirement", 
    #                     foreign_keys=[treeID])
    rfID = Column(Integer, ForeignKey('designsolution.id', ondelete="CASCADE", name="fk_rf_id"))
    is_solved_by = relationship("DesignSolution", 
                        backref="isb", 
                        foreign_keys=[DesignSolution.isbID])

    def __repr__(self):
        return "<FR(name='%s', treeID='%s', rf_parentDSid='%s')>" % (self.name, self.treeID, self.rfID)

    ## function for recursive generation of alternative concepts
    def alternativeSolutions(self):
        # returns a list of dicts with each DNA, including self
        # each dna includes all DS IDs of an instance
        # compiles all DS' alternatives (adding all the DS dna to the allDNA list, and adding thisFR:respectiveDS on top.

        ################ BUG REPORT: ####################
        ## THis entire mechanism fails if there are FR without DS! Always have at least a dummy-DS!
        #################################################

        # allDNA collect's all the alternative's DNA, one alternative per entry in the list:
        allDNA = []

        for d in self.is_solved_by:
            # cerating the individual dna sequence for this FR:DS pair (but only their names):
            #print(d)
            thisDNA = d.id
            # checking if there are any sub-configs for this DS, then we need to add the individual sequence to the end of EACH of the configuration's dna:
            if d.alternativeConfigurations():
                for dsDNA in d.alternativeConfigurations():
                    # print("dsDNA: {}; thisDNA: {}".format(dsDNA, thisDNA))
                    # add tp the respective sequence:
                    dsDNA.append(thisDNA)
                    # print("dsDNA, combined: {}".format(dsDNA))
                    # add the sequnce to the collectors:
                    allDNA.append(dsDNA)
                # print('we append sth; allDNA: {}'.format(allDNA))
            else:
                # if we are at the bottom of the tree, i.e. the DS has no FR below it, it doesn't return an array.
                # so we need to make a new line DNA sequence!
                allDNA.append(thisDNA)

        # returns the collector of all DNA:
        return allDNA

class DesignParameter(Base):
    """
    parameters to be linked to a DS
    """
    __tablename__ = "designparameter"    
    id = Column(Integer, primary_key = True)
    name = Column(String(200))
    value = Column(String(200))
    unit = Column(String(200))
    # tree link:
    treeID = Column(Integer, 
                        ForeignKey('tree.id', 
                            ondelete="CASCADE", 
                            name="fk_dp_tree")
                        )
    dsID = Column(Integer, 
                        ForeignKey('designsolution.id', 
                            ondelete="CASCADE",
                            name="fk_dp_ds")
                        )
    
class InteractsWith(Base):
    """
    iw between two DS, directional 
    """
    __tablename__ = "interactswith" 
    id = Column(Integer, primary_key = True)
    fromDsID = Column(Integer, 
                        ForeignKey('designsolution.id', 
                            ondelete="CASCADE",
                            name="fk_iwOut_id")
                        )
    toDsID = Column(Integer, 
                        ForeignKey('designsolution.id', 
                            ondelete="CASCADE",
                            name="fk_iwIn_id")
                        )
    iwType = Column(String(20))
    treeID = Column(Integer,
                        ForeignKey('tree.id',
                            ondelete="CASCADE",
                            name="fk_iw_id")
                        )
