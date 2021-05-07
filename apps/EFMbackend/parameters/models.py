from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, LargeBinary, Boolean
from sqlalchemy.orm import relationship

# imports from other models:
from apps.EFMbackend.models import Tree, DesignSolution

Base = declarative_base()

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