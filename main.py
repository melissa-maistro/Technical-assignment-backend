from fastapi import FastAPI
from pydantic import BaseModel
from collections import defaultdict
import uuid
import time


app = FastAPI()


users: dict[str, dict] = {}
request_log: dict[str, list] = defaultdict(list)


class User(BaseModel):
    name: str
    
class Request(BaseModel):
    user_id: str


@app.post("/users/", status_code=201)
def create_user(user: User):
    user_id = str(uuid.uuid4())
    users[user_id] = {"id": user_id, "name": user.name, "created_at": time.time()}
    return users[user_id]

@app.post("/requests/", status_code=201)
def make_request(request: Request):
    pass

@app.get("/users/{user_id}/quota")
def get_quota(user_id: str):
    pass