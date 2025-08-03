from fastapi import FastAPI
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router
from app.routers.items import router as items_router
from app.routers.orders import router as orders_router
from app.routers.restaurant import router as restaurant_router

app = FastAPI(title="Quickbite API", description="Quickbite API", version="0.0.1")


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(items_router)
app.include_router(orders_router)
app.include_router(restaurant_router)

@app.get("/")
async def root():
    return {"message": "Hello World"}
