from fastapi import FastAPI
from app.routers import youtube
from fastapi_cors import CORS

app = FastAPI()


origins = ["*"]

app.add_middleware(
    CORS,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(youtube.router, prefix="/youtube", tags=["youtube"])


@app.get("/")
def read_root():
    return {"msg": "Hello World"}
