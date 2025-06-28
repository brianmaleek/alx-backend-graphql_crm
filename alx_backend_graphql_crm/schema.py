import graphene
from crm.schema import Query as CrmQuery, Mutation as CrmMutation

""" class Query(graphene.ObjectType):
    # Define your query fields here
    hello = graphene.String()

    def resolve_hello(self, info):
        return "Hello, GraphQL!" """
class Query(CrmQuery, graphene.ObjectType):
    """
    The root Query class for the GraphQL API, combining CRM queries.
    """
    pass
class Mutation(CrmMutation, graphene.ObjectType):
    """
    The root Mutation class for the GraphQL API, combining CRM mutations.
    """
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)
