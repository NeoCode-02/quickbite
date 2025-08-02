from fastapi import FastAPI
from app.routers import auth

app = FastAPI(title="Quickbite API", description="Quickbite API", version="0.0.1")


app.include_router(auth.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
