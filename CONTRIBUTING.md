Step 1: Clone the Repository:

git clone https://github.com/your-username/project-name.git  
cd project-name  

Step 2: Install Dependencies:

##(frontend)
npm install  
(backend)

python -m venv env(Create a virtual environment and activate it) 
source env/bin/activate 
pip install uvicorn.

(database)

Install PostgreSQL.

Set a password for the postgres user.
Make note of the port (default is 5432).
Connect to PostgreSQL Locally.
psql -U postgres.
Create a Database(save the name for .env file).
Update Your App's .env.

Migrate the database using

 (alembic upgrade head).