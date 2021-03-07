from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, LargeBinary, Boolean
from sqlalchemy.orm import relationship

from apps.EFMbackend.database import Base

class Project(Base):
    """
    parent class to associate all elements of one tree to
    contains multiple concepts
    """
    __tablename__ = "project"
    id = Column(Integer, primary_key = True)
    name = Column(String(200))
    description = Column(String(2000))
    topLvlDSid = Column(Integer, 
                    ForeignKey('designsolution.id', 
                        name="fk_topLvlDS"),
                    nullable=True,)
    # allDS = relationship("DesignSolution", 
    #                 backref="project",
    #                 foreign_keys="designsolution.projectID" 
    #                 )
    # allFR = relationship("FunctionalRequirement", 
    #                 backref="project", 
    #                 )
    # allConcepts = relationship("Concept", 
    #                 backref="project", 
    #                 )
    ##### topLvlDS relationship doesn't work because pydantic crashes with circular relations!
    # topLvlDS = relationship('DesignSolution', 
    #     uselist=False, 
    #     foreign_keys=[topLvlDSid])

    def __repr__(self):
        return "<Project(name='%s')>" % (self.name)

class Concept(Base):
    """
    one instance of a tree of a project
    """
    __tablename__ = "concept"
    id = Column(Integer, primary_key = True)
    name = Column(String(200))
    # project link:
    projectID = Column(Integer, 
                        ForeignKey('project.id', 
                            ondelete="CASCADE", 
                            name="fk_concept_project")
                        )
    # project = relationship("Project", 
    #                 backref="concept", 
    #                 foreign_keys=[projectID])
    def __repr__(self):
        return "<Concept(name='%s', projectID='%s', )>" % (self.name, self.projectID)
    

class DesignSolution(Base):
    """
    DS element for EF-M modelling; contains all basic information
    """
    __tablename__ = "designsolution"
    id = Column(Integer, primary_key = True)
    name = Column(String(200))
    description = Column(String(2000))
    # project link:
    projectID = Column(Integer, 
                        ForeignKey('project.id', 
                            ondelete="CASCADE", 
                            name="fk_ds_project"), 
                        nullable = True)
    # project = relationship("Project", 
    #                     backref="designsolution", 
    #                     foreign_keys=[projectID])
    # isb: 
    isbID = Column(Integer, 
        ForeignKey('functionalrequirement.id',
                            ondelete="CASCADE", 
                            name="fk_isb_id"),
                        nullable=True)
    isb = relationship("FunctionalRequirement", 
                        backref="is_solved_by", 
                        foreign_keys=[isbID])
    # identifier if top-level-node of a project
    #### fix because pydantic doesn't allow circular loops =()
    is_top_level_DS = Column(Boolean, default=False)

    def __repr__(self):
        return "<DS(name='%s', projectID='%s', isb_parentFRid='%s')>" % (self.name, self.projectID, self.isbID)

class FunctionalRequirement(Base):
    """
    FR element for EF-M modelling; contains all basic information
    """
    __tablename__ = "functionalrequirement"
    id = Column(Integer, primary_key = True)
    name = Column(String(200))
    description = Column(String(2000))
    # project link:
    projectID = Column(Integer, 
                        ForeignKey('project.id', 
                            ondelete="CASCADE", 
                            name="fk_fr_project")
                        )
    # project = relationship("Project", 
    #                     backref="functionalrequirement", 
    #                     foreign_keys=[projectID])
    rfID = Column(Integer, ForeignKey('designsolution.id', ondelete="CASCADE", name="fk_rf_id"))
    rf = relationship("DesignSolution", 
                        backref="requires_functions", 
                        foreign_keys=[rfID])

    def __repr__(self):
        return "<FR(name='%s', projectID='%s', rf_parentDSid='%s')>" % (self.name, self.projectID, self.rfID)

    