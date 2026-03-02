from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from collections import defaultdict
import uuid
import time


app = FastAPI()


users: dict[str, dict] = {}
request_log: dict[str, list] = defaultdict(list)

WINDOW_SECONDS = 60
MAX_REQUESTS = 10

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
    user_id = request.user_id
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    
    # check requests from user and only keep the ones made in the last 60 seconds
    cutoff = time.time() - WINDOW_SECONDS
    request_log[user_id] = [t for t in request_log[user_id] if t > cutoff]
    
    # if more than 10 raise exception
    if len(request_log[user_id]) > MAX_REQUESTS:
        raise HTTPException(status_code=429, detail="Too many requests")
    
    request_log[user_id].append(time.time())
    return {"id": user_id, "requests": request_log[user_id]}

@app.get("/users/{user_id}/quota")
def get_quota(user_id: str):
    pass