from fastapi import FastAPI
from models.models import Base
from database import engine
from contextlib import asynccontextmanager
from routers import users, url_shortener


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.get("/")
def main():
    return {"data": "Hello from url-shortener!"}


app.include_router(users.router)
app.include_router(url_shortener.router)

if __name__ == "__main__":
    main()
