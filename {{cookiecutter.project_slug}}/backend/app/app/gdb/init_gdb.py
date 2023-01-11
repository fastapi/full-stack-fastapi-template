import inspect
from neomodel import StructuredNode, ClientError, install_labels, db

# from neomodel import config
# from app.core.config import settings

import app.models

# from app.gdb import NeomodelConfig

# NeomodelConfig().ready()

# config.DATABASE_URL = "bolt://neo4j:neo4j@127.0.0.1:7687"
# config.FORCE_TIMEZONE = settings.NEO4J_FORCE_TIMEZONE
# config.MAX_CONNECTION_POOL_SIZE = settings.NEO4J_MAX_CONNECTION_POOL_SIZE


def createNodeIndices():
    """Create indexes for:
            Node: field_name1, field_name2
    With analyzer: StandardAnalyzer ('standard')
    Update as required.
    """
    indices = [
        # ("indexname1", "Node", "field_name1", "simple"),
        # ("indexname2", "Node", "field_name2" , "standard"),
    ]
    for (index, node, key, analyzer) in indices:
        try:
            q = f"CALL db.index.fulltext.createNodeIndex('{index}',['{node}'],['{key}'], {{analyzer: '{analyzer}'}})"
            db.cypher_query(q)
        except ClientError:
            pass


def dropNodeIndices():
    indices = ["indexname1", "indexname2"]
    for index in indices:
        try:
            q = f"CALL db.index.fulltext.drop('{index}')"
            db.cypher_query(q)
        except ClientError:
            pass


def init_gdb() -> None:
    # Neo4j / neomodel requires nodes to be created, but labels on the nodes
    # can be created at run-time without a specific migration step
    # https://stackoverflow.com/questions/1796180/how-can-i-get-a-list-of-all-classes-within-current-module-in-python
    for node in [
        node
        for _, node in inspect.getmembers(app.models)
        if inspect.isclass(node) and issubclass(node, (StructuredNode))
    ]:
        try:
            install_labels(node)
        except ClientError as e:
            if not str(e.message).lower().startswith("an equivalent constraint already exists"):
                raise e
    # createNodeIndices()

