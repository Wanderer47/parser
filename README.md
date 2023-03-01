docker-compose up --build

docker-compose run app alembic revision --autogenerate -m '<< revision name >>'

docker-compose up app
