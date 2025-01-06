#!/usr/bin/env bash

# install graphviz: brew install graphviz

eralchemy -i "postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_SERVER}:${POSTGRES_PORT}/${POSTGRES_DB}" -o erd.png
