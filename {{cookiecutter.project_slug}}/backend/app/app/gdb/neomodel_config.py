from neomodel import config

from app.core.config import settings


class NeomodelConfig:
    def read_settings(self) -> None:
        # https://stackoverflow.com/a/64309171/295606
        # https://stackoverflow.com/a/66408057/295606
        # https://community.neo4j.com/t/troubleshooting-connection-issues-to-neo4j/129/10
        # Docker very non-obvious ... reach neo4j container by calling the container name
        config.DATABASE_URL = settings.NEO4J_BOLT_URL
        config.FORCE_TIMEZONE = settings.NEO4J_FORCE_TIMEZONE
        config.AUTO_INSTALL_LABELS = settings.NEO4J_AUTO_INSTALL_LABELS
        config.MAX_CONNECTION_POOL_SIZE = settings.NEO4J_MAX_CONNECTION_POOL_SIZE

    def ready(self) -> None:
        self.read_settings()
