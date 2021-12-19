#! /usr/bin/env bash

# Let the DB start
python /app/app/backend_pre_start.py

### 程序出错，无法启动，可以去掉注释，引入这一行
# tail /dev/null -f

# Run migrations
alembic upgrade head

# Create initial data in DB
python /app/app/initial_data.py
