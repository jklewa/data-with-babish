import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from sqlalchemy import func

import models


class Guest(SQLAlchemyObjectType):

    class Meta:
        model = models.Guest
        interfaces = (relay.Node, )


class Reference(SQLAlchemyObjectType):

    class Meta:
        model = models.Reference
        interfaces = (relay.Node, )


class Show(SQLAlchemyObjectType):

    class Meta:
        model = models.Show
        interfaces = (relay.Node, )


class Episode(SQLAlchemyObjectType):

    class Meta:
        model = models.Episode
        interfaces = (relay.Node, )


class Recipe(SQLAlchemyObjectType):

    class Meta:
        model = models.Recipe
        interfaces = (relay.Node, )


class SearchResult(graphene.Union):

    class Meta:
        types = (Guest, Reference, Show, Episode, Recipe)


class Query(graphene.ObjectType):
    node = relay.Node.Field()

    guest = relay.Node.Field(Guest)
    all_guests = SQLAlchemyConnectionField(Guest)

    reference = relay.Node.Field(Reference)
    all_references = SQLAlchemyConnectionField(Reference)

    show = relay.Node.Field(Show)
    all_shows = SQLAlchemyConnectionField(Show)

    episode = relay.Node.Field(Episode)
    all_episodes = SQLAlchemyConnectionField(Episode)

    recipe = relay.Node.Field(Recipe)
    all_recipes = SQLAlchemyConnectionField(Recipe)

    search = graphene.List(SearchResult, q=graphene.String())

    def resolve_search(self, info, q=None):
        guest_query = Guest.get_query(info)
        reference_query = Reference.get_query(info)
        show_query = Show.get_query(info)
        episode_query = Episode.get_query(info)
        recipe_query = Recipe.get_query(info)

        q = ' <-> '.join(
            f'{i}:*' for i in q.lower().split(' ')
        )

        guests = guest_query.filter((models.Guest.name.match(q))).all()

        references = reference_query.filter((models.Reference.name.match(q))).all()

        shows = show_query.filter((models.Show.name.match(q))).all()

        episodes = episode_query.filter((models.Episode.name.match(q))).all()

        recipes = recipe_query.filter((models.Recipe.name.match(q))).all()

        return guests + references + shows + episodes + recipes


schema = graphene.Schema(query=Query, types=[Guest, Reference, Show, Episode, Recipe])
