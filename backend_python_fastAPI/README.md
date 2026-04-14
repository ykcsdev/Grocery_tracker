# LT Groceries tracker

python -m uvicorn app.main:app --reload

http://127.0.0.1:8000/docs

docker run --name grocery-db -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=grocery -p 5432:5432 -d postgres:15


docker ps

docker start grocery-db