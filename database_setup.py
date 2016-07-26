import sys

from sqlalchemy import Column, ForeignKey, Integer, String

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

Base = declarative_base()

class Category(Base):
	__tablename__ = 'categories'
	id = Column(Integer, primary_key=True)
	name = Column(String(120), nullable=False)

class Item(Base):
	__tablename__ = 'category_items'
	id = Column(Integer, primary_key=True)
	name = Column(String, nullable=False)
	description = Column(String)
	category_id = Column(Integer, ForeignKey('categories.id'))
	category = relationship(Category)

####### EOF #######
engine = create_engine(
	'sqlite:///categoryitem.db'
)

Base.metadata.create_all(engine)
