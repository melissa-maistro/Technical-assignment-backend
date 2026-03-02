from fastapi import FastAPI
from pydantic import BaseModel
from collections import defaultdict


app = FastAPI()


users: dict[str, dict] = {}
request_log: dict[str, list] = defaultdict(list)


class User(BaseModel):
    name: str
    
class Request(BaseModel):
    user_id: str


@app.post("/users/", status_code=201)
def create_user(user: User):
    pass

@app.post("/requests/", status_code=201)
def make_request(request: Request):
    pass

@app.get("/users/{user_id}/quota")
def get_quota(user_id: str):
    pass