# coding: utf-8
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, Text, text
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
Base = db.Model
metadata = Base.metadata


class Guest(Base):
    __tablename__ = 'guest'

    id = Column(Integer, primary_key=True, server_default=text("nextval('guest_id_seq'::regclass)"))
    name = Column(String, nullable=False)

    def serialize(self, related=True):
        return {
            'guest_id': self.id,
            'name': self.name,
            **({
                'appearances': [
                    e.serialize(False)
                    for e in self.appearances
                ]
            } if related else {})
        }


class Reference(Base):
    __tablename__ = 'reference'

    id = Column(Integer, primary_key=True, server_default=text("nextval('reference_id_seq'::regclass)"))
    type = Column(String)
    name = Column(String)
    description = Column(Text)
    external_link = Column(String)

    def serialize(self, related=True):
        return {
            'reference_id': self.id,
            'type': self.type,
            'name': self.name,
            'description': self.description,
            'external_link': self.external_link,
            **({
                'episodes_inspired': [
                    e.serialize(False)
                    for e in self.episodes_inspired
                ]
            } if related else {})
        }


class Show(Base):
    __tablename__ = 'show'

    id = Column(Integer, primary_key=True, server_default=text("nextval('show_id_seq'::regclass)"))
    name = Column(String, nullable=False, unique=True)

    def serialize(self, related=True):
        return {
            'show_id': self.id,
            'name': self.name,
        }


class Episode(Base):
    __tablename__ = 'episode'

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    youtube_link = Column(String, nullable=False)
    official_link = Column(String, nullable=False)
    published_date = Column(DateTime(True))
    show_id = Column(ForeignKey('show.id'), nullable=False)
    image_link = Column(String)

    show = relationship('Show')
    guests = relationship('Guest', secondary='guest_appearances',
                          backref='appearances')
    references = relationship('Reference', secondary='episode_inspired_by',
                              backref='episodes_inspired')
    recipes = relationship('Recipe',
                           backref='episode')

    def serialize(self, related=True):
        return {
            'episode_id': self.id,
            'name': self.name,
            'youtube_link': self.youtube_link,
            'official_link': self.official_link,
            'image_link': self.image_link,
            **({
                'related': {
                    'show': self.show.serialize(False),
                    'guests': [
                        g.serialize(False)
                        for g in self.guests
                    ],
                    'inspired_by': [
                        r.serialize(False)
                        for r in self.references
                    ],
                    'recipes': [
                        r.serialize(False)
                        for r in self.recipes
                    ],
                }
            } if related else {})
        }


t_episode_inspired_by = Table(
    'episode_inspired_by', metadata,
    Column('episode_id', ForeignKey('episode.id'), primary_key=True, nullable=False),
    Column('reference_id', ForeignKey('reference.id'), primary_key=True, nullable=False)
)


t_guest_appearances = Table(
    'guest_appearances', metadata,
    Column('episode_id', ForeignKey('episode.id')),
    Column('guest_id', ForeignKey('guest.id'))
)


class Recipe(Base):
    __tablename__ = 'recipe'

    id = Column(Integer, primary_key=True, server_default=text("nextval('recipe_id_seq'::regclass)"))
    name = Column(String, nullable=False)
    raw_ingredient_list = Column(Text, nullable=False)
    raw_procedure = Column(Text, nullable=False)
    episode_id = Column(ForeignKey('episode.id'), nullable=False)

    def serialize(self, related=True):
        return {
            'recipe_id': self.id,
            'name': self.name,
            'raw_ingredient_list': self.raw_ingredient_list,
            'raw_procedure': self.raw_procedure,
            **({
                'source': self.episode.serialize(False)
            } if related else {})
        }
