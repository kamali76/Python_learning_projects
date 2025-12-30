from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class addRequest(BaseModel):
    a: int
    b: int
    user1: str
    user2: str


@app.get("/health")
def healthCheck():
    return {"status": "ok"}

@app.post("/add")
def addNum(data: addRequest):
    return {"result": data.a+data.b}

@app.get("/getusers")
async def getUsers(data: addRequest):
    return {"user1": data.user1, "user2": data.user2}