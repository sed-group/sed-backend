from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, LargeBinary, Boolean
from sqlalchemy.orm import relationship

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
                        name="fk_topLvlDS"),
                    nullable=True,)
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
    ##### topLvlDS relationship doesn't work because pydantic crashes with circular relations!
    # topLvlDS = relationship('DesignSolution', 
    #     uselist=False, 
    #     foreign_keys=[topLvlDSid])

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
    # identifier if top-level-node of a tree
    #### fix because pydantic doesn't allow circular loops =()
    is_top_level_DS = Column(Boolean, default=False)

    def __repr__(self):
        return "<DS(name='%s', treeID='%s', isb_parentFRid='%s')>" % (self.name, self.treeID, self.isbID)

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
    ds = Column(Integer, 
                        ForeignKey('designsolution.id', 
                            ondelete="CASCADE",
                            name="fk_dp_id")
                        )

    
# class InteractsWith(Base):
#     id = Column(Integer, primary_key = True)
#     fromDs = Column(Integer, 
#                         ForeignKey('designsolution.id', 
#                             ondelete="CASCADE",
#                             name="fk_iwOut_id")
#                         )
#     toDs = Column(Integer, 
#                         ForeignKey('designsolution.id', 
#                             ondelete="CASCADE",
#                             name="fk_iwIn_id")
#                         )
#     iwType = Column(String(20))
