from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Base, Item

engine = create_engine('sqlite:///categoryitem.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

category1 = Category(name="Guitar")
session.add(category1)
session.commit()

strings = Item(name="Ernie Ball Strings", description="These are some of the best string for electric guitar",
				category=category1)
session.add(strings)
session.commit()

acoustic = Item(name="Acoustic Guitar", description="Hollow body guitar with the need for an amplifier",
				category=category1)
session.add(acoustic)
session.commit()

electric = Item(name="Electric Guitar", description="Solid body guitar that shreds.  Needs an amplifier.",
				category=category1)
session.add(electric)
session.commit()

category2 = Category(name="Fitness")
session.add(category2)
session.commit()

crossfit = Item(name="Crossfit", description="Crossfit is high-intensity fitness.  Crossfit combines high reps with olympic-style lifts.",
				category=category2)
session.add(crossfit)
session.commit()

bodybuilding = Item(name="Bodybuilding", description="Bodybuilding is lifting for the sake of reaching peak aesthetics",
				category=category2)
session.add(bodybuilding)
session.commit()
