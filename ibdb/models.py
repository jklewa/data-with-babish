# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, String, Table, Text, text, Date, UniqueConstraint
from sqlalchemy.orm import relationship, backref
from flask_sqlalchemy import SQLAlchemy
from flask import request

from ibdb.recipe_parser import RecipeParser

db = SQLAlchemy()
Base = db.Model
metadata = Base.metadata


class Guest(Base):
    __tablename__ = 'guest'

    id = Column(Integer, primary_key=True, server_default=text("nextval('guest_id_seq'::regclass)"))
    name = Column(String, nullable=False, unique=True)
    image_link = Column(String)

    def serialize(self, related=True):
        return {
            'self': f'{request.host_url[:-1]}/guest/{self.id}',
            'guest_id': self.id,
            'name': self.name,
            'image_link': self.image_link,
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
    name = Column(String, unique=True)
    description = Column(Text)
    external_link = Column(String)
    image_link = Column(String)

    def serialize(self, related=True):
        return {
            'self': f'{request.host_url[:-1]}/reference/{self.id}',
            'reference_id': self.id,
            'type': self.type,
            'name': self.name,
            'description': self.description,
            'external_link': self.external_link,
            'image_link': self.image_link,
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
    image_link = Column(String)

    def serialize(self, related=True):
        return {
            'self': f'{request.host_url[:-1]}/show/{self.id}',
            'show_id': self.id,
            'name': self.name,
            'image_link': self.image_link,
            **({
                'episodes': [
                    e.serialize(False)
                    for e in self.episodes
                ]
            } if related else {})
        }


class Episode(Base):
    __tablename__ = 'episode'
    __table_args__ = (
        UniqueConstraint('name', 'show_id', name='episode_name_show_uindex'),
    )

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    youtube_link = Column(String, nullable=False)
    official_link = Column(String, nullable=False)
    image_link = Column(String)
    published_date = Column(Date())
    show_id = Column(ForeignKey('show.id'), nullable=False)

    _backref_order_by = 'Episode.published_date.desc(),Episode.id'

    show = relationship('Show',
                        uselist=False,
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
                                           uselist=False,
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
    Column('reference_id', ForeignKey('reference.id'), primary_key=True, nullable=False),
)


t_guest_appearances = Table(
    'guest_appearances', metadata,
    Column('episode_id', ForeignKey('episode.id'), primary_key=True, nullable=False),
    Column('guest_id', ForeignKey('guest.id'), primary_key=True, nullable=False),
)


class Recipe(Base):
    __tablename__ = 'recipe'

    id = Column(Integer, primary_key=True, server_default=text("nextval('recipe_id_seq'::regclass)"))
    name = Column(String, nullable=False)
    image_link = Column(String)
    raw_ingredient_list = Column(Text, nullable=False)
    raw_procedure = Column(Text, nullable=False)
    episode_id = Column(ForeignKey('episode.id'), nullable=False)

    def serialize(self, related=True):
        return {
            'self': f'{request.host_url[:-1]}/recipe/{self.id}',
            'recipe_id': self.id,
            'name': self.name,
            'image_link': self.image_link,
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
            if 'For the ' not in i
        ]


'''
Helper methods for models
'''
# TODO: refactor to use ORM


def upsert_episode(session, episode):
    # test if we will be creating this
    result = session.execute(
        """
            SELECT id FROM episode WHERE id = :id
        """,
        {k: episode[k] for k in ('id',)}
    )
    created = True
    if result.rowcount > 0:
        created = False

    # upsert
    session.execute(
        """
            INSERT INTO episode (id, name, youtube_link, official_link, image_link, published_date, show_id)
            VALUES (:id, :name, :youtube_link, :official_link, :image_link, :published_date, :show_id)
            ON CONFLICT (id)
            DO UPDATE SET (name, youtube_link, official_link, image_link, published_date, show_id)
            = (EXCLUDED.name, EXCLUDED.youtube_link, EXCLUDED.official_link, EXCLUDED.image_link, EXCLUDED.published_date, EXCLUDED.show_id)
        """,
        {k: episode[k] for k in ('id', 'name', 'youtube_link', 'official_link', 'image_link', 'published_date', 'show_id')})
    return episode['id'], created


def upsert_reference(session, reference):
    result = session.execute(
        """
            SELECT id FROM reference WHERE name = :name
        """,
        {k: reference[k] for k in ('name',)}
    )
    if result.rowcount == 0:
        result = session.execute(
            """
                INSERT INTO reference (name)
                VALUES (:name)
                RETURNING id
            """,
            {k: reference[k] for k in ('name',)}
        )
    reference_id = result.fetchone()[0]
    return reference_id


def upsert_episode_inspired_by(session, episode_id, reference_id):
    session.execute(
        """
            INSERT INTO episode_inspired_by (episode_id, reference_id)
            VALUES (:episode_id, :reference_id)
            ON CONFLICT (episode_id, reference_id)
            DO NOTHING
        """,
        {'episode_id': episode_id, 'reference_id': reference_id}
    )


def upsert_guest(session, guest):
    result = session.execute(
        """
            SELECT id FROM guest WHERE name = :name
        """,
        {k: guest[k] for k in ('name',)}
    )
    if result.rowcount == 0:
        result = session.execute(
            """
                INSERT INTO guest (name)
                VALUES (:name)
                RETURNING id
            """,
            {k: guest[k] for k in ('name',)}
        )
    reference_id = result.fetchone()[0]
    return reference_id


def upsert_guest_appearance(session, episode_id, guest_id):
    session.execute(
        """
            INSERT INTO guest_appearances (episode_id, guest_id)
            VALUES (:episode_id, :guest_id)
            ON CONFLICT (episode_id, guest_id)
            DO NOTHING
        """,
        {'episode_id': episode_id, 'guest_id': guest_id}
    )


def count_episode_recipes(session, episode_id):
    result = session.execute(
        """
            SELECT id FROM recipe WHERE episode_id = :episode_id
        """,
        {'episode_id': episode_id}
    )
    return result.rowcount


def upsert_recipe(session, recipe):
    result = session.execute(
        """
            SELECT id FROM recipe WHERE episode_id = :episode_id AND name = :name
        """,
        {k: recipe[k] for k in ('episode_id', 'name')}
    )
    if result.rowcount == 0:
        result = session.execute(
            """
                INSERT INTO recipe (episode_id, name, image_link, raw_ingredient_list, raw_procedure)
                VALUES (:episode_id, :name, :image_link, :raw_ingredient_list, :raw_procedure)
                RETURNING id
            """,
            {k: recipe[k] for k in ('episode_id', 'name', 'image_link', 'raw_ingredient_list', 'raw_procedure')}
        )
    recipe_id = result.fetchone()[0]
    return recipe_id
