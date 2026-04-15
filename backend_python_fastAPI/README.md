# LT Groceries tracker

python -m uvicorn app.main:app --reload

http://127.0.0.1:8000/docs

docker run --name grocery-db -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=grocery -p 5432:5432 -d postgres:15

docker exec -it grocery_tracker-db-1 psql -U postgres -c "DROP DATABASE grocery;"
docker exec -it grocery_tracker-db-1 psql -U postgres -c "CREATE DATABASE grocery;"

docker exec grocery-db pg_dump -U postgres -d grocery --clean --if-exists | docker exec -i grocery_tracker-db-1 psql -U postgres -d grocery

docker ps

docker start grocery-db