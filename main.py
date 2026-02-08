from fastapi import FastAPI
from routers.api import admin
from contextlib import asynccontextmanager
from database import Base, engine
from routers.api import (
    admin as admin_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(admin_router.router)


def main():
    print("Hello from codeatlas!")


if __name__ == "__main__":
    main()
