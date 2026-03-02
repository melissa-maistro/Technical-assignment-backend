from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from collections import defaultdict
import uuid
import time


app = FastAPI()

# in-memory storage
users: dict[str, dict] = {}
request_log: dict[str, list] = defaultdict(list)

WINDOW_SECONDS = 60
MAX_REQUESTS = 10

# ---------------------------- PYDANTIC MODELS -----------------------------------
class User(BaseModel):
    name: str
    
class Request(BaseModel):
    user_id: str

# ---------------------------- HELPER FUNCTION ------------------------------------

def prune_expired_requests(user_id: str):
    cutoff = time.time() - WINDOW_SECONDS
    request_log[user_id] = [t for t in request_log[user_id] if t > cutoff]

# ------------------------------ ENDPOINTS ----------------------------------------

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
    prune_expired_requests(user_id)
    
    # if more than 10 raise exception
    if len(request_log[user_id]) >= MAX_REQUESTS:
        raise HTTPException(status_code=429, detail="Too many requests")
    
    request_log[user_id].append(time.time())
    return {"id": user_id, "requests": request_log[user_id]}


@app.get("/users/{user_id}/quota")
def get_quota(user_id: str):
    if user_id not in users:
        raise HTTPException(status_code=404, detail="User not found")
    
    prune_expired_requests(user_id)
    
    return {
        "requests_used": len(request_log[user_id]),
        "requests_remaining": MAX_REQUESTS - len(request_log[user_id]),
        "limit": MAX_REQUESTS,
        "window_seconds": WINDOW_SECONDS
    }