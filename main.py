from fastapi import FastAPI

app = FastAPI(
    title="Quickbite API",
    description="Quickbite API",
    version="0.0.1"
)

async def root():
    return {"message" : "Hello World"}
    