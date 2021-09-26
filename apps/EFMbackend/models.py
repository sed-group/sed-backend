from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, LargeBinary, Boolean
from sqlalchemy.orm import relationship


# import EF-M sub models
# from .parameters.models import DesignParameter

Base = declarative_base()

class Tree(Base):
    """
    parent class to associate all elements of one tree to
    contains multiple concepts
    """
    __tablename__ = "tree"
    id = Column(Integer, primary_key = True)
    subproject_id = Column(Integer) # links to core subprojects
    name = Column(String(200))
    description = Column(String(2000))
    top_level_ds_id = Column(Integer, 
                    ForeignKey('designsolution.id', 
                        ondelete="SET NULL",
                        name="fk_topLvlDS"
                        ),
                    nullable=True,
                    )
    #### topLvlDS relationship doesn't work because pydantic crashes with circular relations!
    top_level_ds = relationship('DesignSolution', 
        uselist=False, 
        foreign_keys=[top_level_ds_id])

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
    tree_id = Column(Integer, 
                        ForeignKey('tree.id', 
                            ondelete="CASCADE", 
                            name="fk_concept_tree")
                        )
    # tree = relationship("Tree", 
    #                 backref="concept", 
    #                 foreign_keys=[tree_id])
    dna = Column(String(2000)) # List of all IDs of the DS in this concept
    def __repr__(self):
        return "<Concept(name='%s', tree_id='%s', )>" % (self.name, self.tree_id)
    
class DesignSolution(Base):
    """
    DS element for EF-M modelling; contains all basic information
    """
    __tablename__ = "designsolution"
    id = Column(Integer, primary_key = True)
    name = Column(String(200))
    description = Column(String(2000))
    # tree link:
    tree_id = Column(Integer, 
                        ForeignKey('tree.id', 
                            ondelete="CASCADE", 
                            name="fk_ds_tree"), 
                        nullable = True)
    # tree = relationship("Tree", 
    #                     backref="designsolution", 
    #                     foreign_keys=[tree_id])
    # isb: 
    isb_id = Column(Integer, 
        ForeignKey('functionalrequirement.id',
                            ondelete="CASCADE", 
                            name="fk_isb_id"),
                        nullable=True)
    requires_functions = relationship("FunctionalRequirement", 
                        backref="rf", 
                        foreign_keys='[FunctionalRequirement.rf_id]')
    interacts_with = relationship("InteractsWith",
                        backref="fromDS",
                        foreign_keys='[InteractsWith.from_ds_id]')
    design_parameters = relationship("DesignParameter",
                        backref="ds",
                        foreign_keys='[DesignParameter.ds_id]')
    # identifier if top-level-node of a tree
    #### fix because pydantic doesn't allow circular loops =()
    is_top_level_ds = Column(Boolean, default=False)

    def __repr__(self):
        return "<DS(name='%s', tree_id='%s', isb_parentFRid='%s')>" % (self.name, self.tree_id, self.isb_id)
           
class FunctionalRequirement(Base):
    """
    FR element for EF-M modelling; contains all basic information
    """
    __tablename__ = "functionalrequirement"
    id = Column(Integer, primary_key = True)
    name = Column(String(200))
    description = Column(String(2000))
    # tree link:
    tree_id = Column(Integer, 
                        ForeignKey('tree.id', 
                            ondelete="CASCADE", 
                            name="fk_fr_tree")
                        )
    # tree = relationship("Tree", 
    #                     backref="functionalrequirement", 
    #                     foreign_keys=[tree_id])
    rf_id = Column(Integer, ForeignKey('designsolution.id', ondelete="CASCADE", name="fk_rf_id"))
    is_solved_by = relationship("DesignSolution", 
                        backref="isb", 
                        foreign_keys=[DesignSolution.isb_id])

    def __repr__(self):
        return "<FR(name='%s', tree_id='%s', rf_parentDSid='%s')>" % (self.name, self.tree_id, self.rf_id)
    
class InteractsWith(Base):
    """
    iw between two DS, directional 
    """
    __tablename__ = "interactswith" 
    id = Column(Integer, primary_key = True)
    from_ds_id = Column(Integer, 
                        ForeignKey('designsolution.id', 
                            ondelete="CASCADE",
                            name="fk_iwOut_id")
                        )
    to_ds_id = Column(Integer, 
                        ForeignKey('designsolution.id', 
                            ondelete="CASCADE",
                            name="fk_iwIn_id")
                        )
    iw_type = Column(String(20))
    tree_id = Column(Integer,
                        ForeignKey('tree.id',
                            ondelete="CASCADE",
                            name="fk_iw_id")
                        )
    description = Column(String(2000))

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
    tree_id = Column(Integer, 
                        ForeignKey('tree.id', 
                            ondelete="CASCADE", 
                            name="fk_dp_tree")
                        )
    ds_id = Column(Integer, 
                        ForeignKey('designsolution.id', 
                            ondelete="CASCADE",
                            name="fk_dp_ds")
                        )