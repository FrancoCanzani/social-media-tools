from fastapi import FastAPI
from routers import youtube

app = FastAPI()

app.include_router(youtube.router, prefix="/youtube", tags=["youtube"])


@app.get("/")
def read_root():
    return {"msg": "Hello World"}
