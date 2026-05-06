# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, String, Table, Text, text, Date, UniqueConstraint
from sqlalchemy.orm import relationship, backref
from flask_sqlalchemy import SQLAlchemy

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


class Tag(Base):
    __tablename__ = 'tag'
    __table_args__ = (
        UniqueConstraint('axis', 'name', name='tag_axis_name_uindex'),
    )

    id = Column(Integer, primary_key=True, server_default=text("nextval('tag_id_seq'::regclass)"))
    axis = Column(String, nullable=False)
    name = Column(String, nullable=False)
    external_id = Column(String)

    def serialize(self, related=True):
        return {
            'tag_id': self.id,
            'axis': self.axis,
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
    slug = Column(String)
    youtube_link = Column(String, nullable=False)
    official_link = Column(String, nullable=False)
    image_link = Column(String)
    published_date = Column(Date())
    time_to_cook = Column(Integer)
    yield_qty = Column(Integer)
    yield_unit = Column(String)

    _backref_order_by = 'Episode.published_date.desc(),Episode.id'

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
    tags = relationship('Tag',
                        secondary='episode_tags',
                        order_by='Tag.axis,Tag.name,Tag.id',
                        backref=backref('episodes',
                                        order_by=_backref_order_by))
    recipes = relationship('Recipe', order_by='Recipe.name,Recipe.id',
                           backref=backref('episode',
                                           uselist=False,
                                           order_by=_backref_order_by))

    def serialize(self, related=True):
        return {
            'episode_id': self.id,
            'name': self.name,
            'published_date': self.published_date.isoformat() if self.published_date else None,
            'youtube_link': self.youtube_link,
            'official_link': self.official_link,
            'image_link': self.image_link,
            **({
                'related': {
                    'tags': [
                        t.serialize(False)
                        for t in self.tags
                    ],
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


t_episode_tags = Table(
    'episode_tags', metadata,
    Column('episode_id', ForeignKey('episode.id'), primary_key=True, nullable=False),
    Column('tag_id', ForeignKey('tag.id'), primary_key=True, nullable=False),
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
            'recipe_id': self.id,
            'name': self.name,
            'image_link': self.image_link,
            'raw_ingredient_list': self.raw_ingredient_list,
            'raw_procedure': self.raw_procedure,
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


EPISODE_COLUMNS = (
    'id', 'name', 'slug', 'youtube_link', 'official_link', 'image_link',
    'published_date', 'time_to_cook', 'yield_qty', 'yield_unit',
)


def upsert_episode(session, episode):
    result = session.execute(
        """
            SELECT id FROM episode WHERE id = :id
        """,
        {'id': episode['id']}
    )
    created = result.rowcount == 0

    session.execute(
        """
            INSERT INTO episode (id, name, slug, youtube_link, official_link, image_link,
                                 published_date, time_to_cook, yield_qty,
                                 yield_unit)
            VALUES (:id, :name, :slug, :youtube_link, :official_link, :image_link,
                    :published_date, :time_to_cook, :yield_qty,
                    :yield_unit)
            ON CONFLICT (id)
            DO UPDATE SET (name, slug, youtube_link, official_link, image_link,
                           published_date, time_to_cook, yield_qty,
                           yield_unit)
            = (EXCLUDED.name, EXCLUDED.slug, EXCLUDED.youtube_link, EXCLUDED.official_link,
               EXCLUDED.image_link, EXCLUDED.published_date, EXCLUDED.time_to_cook,
               EXCLUDED.yield_qty, EXCLUDED.yield_unit)
        """,
        {k: episode.get(k) for k in EPISODE_COLUMNS})
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


def upsert_tag(session, tag):
    result = session.execute(
        """
            SELECT id FROM tag WHERE axis = :axis AND name = :name
        """,
        {k: tag[k] for k in ('axis', 'name')}
    )
    if result.rowcount == 0:
        result = session.execute(
            """
                INSERT INTO tag (axis, name, external_id)
                VALUES (:axis, :name, :external_id)
                RETURNING id
            """,
            {'axis': tag['axis'], 'name': tag['name'], 'external_id': tag.get('external_id')}
        )
    tag_id = result.fetchone()[0]
    return tag_id


def upsert_episode_tag(session, episode_id, tag_id):
    session.execute(
        """
            INSERT INTO episode_tags (episode_id, tag_id)
            VALUES (:episode_id, :tag_id)
            ON CONFLICT (episode_id, tag_id)
            DO NOTHING
        """,
        {'episode_id': episode_id, 'tag_id': tag_id}
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
