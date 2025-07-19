from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Noun(Base):
    __tablename__ = "nouns"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    attributes = relationship("Attribute", back_populates="noun")

class Attribute(Base):
    __tablename__ = "attributes"
    
    id = Column(Integer, primary_key=True, index=True)
    noun_id = Column(Integer, ForeignKey("nouns.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    noun = relationship("Noun", back_populates="attributes")
    values = relationship("Value", back_populates="attribute")
    
    # Unique constraint on noun_id and name
    __table_args__ = (UniqueConstraint('noun_id', 'name', name='uq_noun_attribute'),)

class Value(Base):
    __tablename__ = "values"
    
    id = Column(Integer, primary_key=True, index=True)
    attribute_id = Column(Integer, ForeignKey("attributes.id"), nullable=False)
    name = Column(String, nullable=False)
    data_type = Column(String, nullable=False)  # string, number, date, boolean
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    attribute = relationship("Attribute", back_populates="values")
    data_entries = relationship("Data", back_populates="value")
    
    # Unique constraint on attribute_id and name
    __table_args__ = (UniqueConstraint('attribute_id', 'name', name='uq_attribute_value'),)

class Data(Base):
    __tablename__ = "data"
    
    id = Column(Integer, primary_key=True, index=True)
    value_id = Column(Integer, ForeignKey("values.id"), nullable=False)
    data_value = Column(Text, nullable=False)  # Store as text, convert based on data_type
    date_recorded = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    value = relationship("Value", back_populates="data_entries") 