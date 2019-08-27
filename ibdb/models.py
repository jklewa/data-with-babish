# coding: utf-8
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, Text, text
from sqlalchemy.orm import relationship, backref
from flask_sqlalchemy import SQLAlchemy
from flask import request

from recipe_parser import RecipeParser

db = SQLAlchemy()
Base = db.Model
metadata = Base.metadata


class Guest(Base):
    __tablename__ = 'guest'

    id = Column(Integer, primary_key=True, server_default=text("nextval('guest_id_seq'::regclass)"))
    name = Column(String, nullable=False)

    def serialize(self, related=True):
        return {
            'self': f'{request.host_url[:-1]}/guest/{self.id}',
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
            'self': f'{request.host_url[:-1]}/reference/{self.id}',
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
            'self': f'{request.host_url[:-1]}/show/{self.id}',
            'show_id': self.id,
            'name': self.name,
            **({
                'episodes': [
                    e.serialize(False)
                    for e in self.episodes
                ]
            } if related else {})
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

    _backref_order_by = 'Episode.published_date.desc(),Episode.id'

    show = relationship('Show',
                        order_by='Show.id',
                        backref=backref('episodes',
                                        order_by=_backref_order_by))
    guests = relationship('Guest',
                          secondary='guest_appearances',
                          order_by='Guest.name,Guest.id',
                          backref=backref('appearances',
                                          order_by=_backref_order_by))
    inspired_by = relationship('Reference',
                               secondary='episode_inspired_by',
                               order_by='Reference.name,Reference.id',
                               backref=backref('episodes_inspired',
                                               order_by=_backref_order_by))
    recipes = relationship('Recipe', order_by='Recipe.name,Recipe.id',
                           backref=backref('episode',
                                           order_by=_backref_order_by))

    def serialize(self, related=True):
        return {
            'self': f'{request.host_url[:-1]}/episode/{self.id}',
            'episode_id': self.id,
            'name': self.name,
            'published_date': self.published_date.isoformat(),
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
                        for r in self.inspired_by
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
            'self': f'{request.host_url[:-1]}/recipe/{self.id}',
            'recipe_id': self.id,
            'name': self.name,
            'raw_ingredient_list': self.raw_ingredient_list,
            'raw_procedure': self.raw_procedure,
            'ingredient_list': self.ingredient_list(),
            **({
                'source': self.episode.serialize(False),
            } if related else {})
        }

    def ingredient_list(self):
        return [
            RecipeParser.parse_ingredient(i)
            for i in self.raw_ingredient_list.splitlines()
            if not 'For the ' in i
        ]
