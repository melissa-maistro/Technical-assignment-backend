# Technical assignment backend

## Project Overview
This is a lightweight backend service developed as part of a technical assignment. It enforces a request limit per user using a rolling window strategy to ensure fair usage.

## Technical Stack
* **Language:** Python
* **Framework:** FastAPI
* **Storage:** In-memory (Python dictionaries and `defaultdict`)
* **Testing:** Pytest with FastAPI TestClient 

## Design Decisions

### 1. Rate Limiting Strategy: Rolling Window
Instead of a fixed window that resets at a specific clock time, I implemented a **Rolling 1-Minute Window**. 
* **Mechanism:** Every time a request is made to `/requests/`, the system prunes timestamps older than 60 seconds for that specific user.
* **Accuracy:** This prevents "bursting" at the edge of a fixed minute (e.g., making 10 requests at 0:59 and another 10 at 1:01), which would technically violate the 10-requests-per-minute rule if viewed as a continuous 60-second slice.

### 2. In-Memory Storage
Since no database was required, I used two primary data structures:
* `users`: A dictionary mapping UUIDs to user metadata.
* `request_log`: A `defaultdict` where each key is a `user_id` and the value is a list of floating-point timestamps representing successful requests.

### 3. Error Handling
* **404 Not Found:** Returned if a request or quota check is attempted for a non-existent user.
* **429 Too Many Requests:** Returned when a user exceeds the limit of 10 requests within the rolling 60-second window.
* **Input Validation:** Handled automatically by Pydantic models to ensure required fields (like `name` or `user_id`) are present.

### 4. UUID User IDs

User IDs are UUID v4s generated server-side. This avoids sequential IDs that could be guessed and also keeps the service free of any authentication layer.

## API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/users/` | Creates a new user and returns a unique UUID. |
| **POST** | `/requests/` | Logs a single request for a user; enforces the 10-request limit. |
| **GET** | `/users/{id}/quota` | Returns the current 1-minute quota details (used vs. remaining). |

## Trade-offs & Known Limitations

* **Memory Efficiency:** While list-based timestamp tracking is highly accurate for small limits (10 requests), it would become inefficient if the limit were scaled to thousands of requests per second. 
* **Distributed Systems:** Because the storage is in-memory, this service is not "stateless". If deployed behind a load balancer with multiple instances, each instance would have its own independent counter. 
* **Pruning Trigger:** Currently, expired requests are pruned only when a user interacts with the API. For a production system with millions of inactive users, a background "cleanup" task might be needed to free up memory.
* **No authentication:** Any caller can create users or submit requests for any user_id.
* **Clock skew:** Relies on `time.time()` of the single process; fine for local/single-server deployment.

## Setup and Testing

### Installation
1. Create a virtual environment and activate it
   ```bash
   python -m venv .venv
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. To run the app
   ```bash
   uvicorn main:app --reload
   ```

4. To run the tests
   ```bash
   pytest -v
   ```