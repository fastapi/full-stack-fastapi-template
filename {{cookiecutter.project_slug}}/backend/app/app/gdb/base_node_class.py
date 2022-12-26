from neomodel import (
    StructuredNode,
    StringProperty,
    BooleanProperty,
    UniqueIdProperty,
    DateTimeProperty,
)
from neomodel.util import classproperty
from datetime import datetime
import pytz


class NodeBase(StructuredNode):
    @property
    def as_dict(self):
        return {
            k: v
            for k, v in self.__dict__.items()
            if v is not None and k in [name for name, _ in self.__all_properties__]
        }

    @classproperty
    def __unique_indexed_properties__(cls):
        return tuple(
            name
            for name, property in cls.defined_properties(aliases=False, rels=False).items()
            if property.unique_index
        )

    @classmethod
    def _build_merge_query(cls, merge_params, update_existing=False, lazy=False, relationship=None):
        """
        Get a tuple of a CYPHER query and a params dict for the specified MERGE query.
        :param merge_params: The target node match parameters, each node must have a "create" key and optional "update".
        :type merge_params: list of dict
        :param update_existing: True to update properties of existing nodes, default False to keep existing values.
        :type update_existing: bool
        :rtype: tuple
        """
        # Modified as per https://github.com/neo4j-contrib/neomodel/issues/575
        query_params = dict(merge_params=merge_params)
        required_properties = cls.__required_properties__
        if update_existing:
            required_properties = cls.__unique_indexed_properties__
        n_merge = "n:{0} {{{1}}}".format(
            ":".join(cls.inherited_labels()),
            ", ".join("{0}: params.create.{0}".format(getattr(cls, p).db_property or p) for p in required_properties),
        )
        if relationship is None:
            # create "simple" unwind query
            query = "UNWIND $merge_params as params\n MERGE ({0})\n ".format(n_merge)
        else:
            # validate relationship
            if not isinstance(relationship.source, StructuredNode):
                raise ValueError("relationship source [{0}] is not a StructuredNode".format(repr(relationship.source)))
            relation_type = relationship.definition.get("relation_type")
            if not relation_type:
                raise ValueError("No relation_type is specified on provided relationship")

            from neomodel.match import _rel_helper

            query_params["source_id"] = relationship.source.id
            query = "MATCH (source:{0}) WHERE ID(source) = $source_id\n ".format(relationship.source.__label__)
            query += "WITH source\n UNWIND $merge_params as params \n "
            query += "MERGE "
            query += _rel_helper(
                lhs="source",
                rhs=n_merge,
                ident=None,
                relation_type=relation_type,
                direction=relationship.definition["direction"],
            )

        query += "ON CREATE SET n = params.create\n "
        # if update_existing, write properties on match as well
        if update_existing is True:
            query += "ON MATCH SET n += params.update\n"

        # close query
        if lazy:
            query += "RETURN id(n)"
        else:
            query += "RETURN n"

        return query, query_params


class MetadataBase(NodeBase):
    # Receive via API
    # https://www.dublincore.org/specifications/dublin-core/dcmi-terms/#section-3
    identifier = UniqueIdProperty()
    title = StringProperty(help_text="A human-readable title given to the resource.")
    description = StringProperty(help_text="A short description of the resource.",)
    # Node-specific labels
    created = DateTimeProperty(default=lambda: datetime.now(pytz.utc))
    isActive = BooleanProperty(default=True, help_text="Is the resource currently updated or maintained.",)
    isPrivate = BooleanProperty(
        default=True, help_text="Is the resource private to team members with appropriate authorisation.",
    )

