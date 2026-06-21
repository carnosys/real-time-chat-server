from fastapi import FastAPI

from app.api.routes import auth, rooms


app = FastAPI()

app.include_router(auth.router)
app.include_router(rooms.router)
