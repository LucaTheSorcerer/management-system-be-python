from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import SessionLocal, Base, engine

load_dotenv()
app = FastAPI()


# Dependency to get DB session
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()


@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        # Optionally, here you can set up your database, e.g., Base.metadata.create_all()
        pass


@app.get("/")
async def root(db: AsyncSession = Depends(get_db)):
    return {"message": "Hello Postgres"}