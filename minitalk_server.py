from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

stored_data = None
stored_result = None


@app.post("/send_data")
async def send_data(req: Request):
    """Client sends its data"""
    global stored_data, stored_result
    body = await req.json()
    stored_data = body.get("data")
    stored_result = None
    print(f"📥 Data received from client: {stored_data}")
    return {"status": "data_received"}


@app.get("/fetch_data")
async def fetch_data():
    """Server node fetches client data"""
    global stored_data
    if stored_data is not None:
        print(f"📤 Sending data to server_dummy: {stored_data}")
        return {"status": "ready", "data": stored_data}
    return {"status": "waiting"}


@app.post("/send_result")
async def send_result(req: Request):
    """Server node sends its result"""
    global stored_result
    body = await req.json()
    stored_result = body.get("result")
    print(f"✅ Result received from server_dummy: {stored_result}")
    return {"status": "result_stored"}


@app.get("/fetch_result")
async def fetch_result():
    """Client fetches final result"""
    global stored_result
    if stored_result is not None:
        print(f"📤 Sending result to client_dummy: {stored_result}")
        return {"status": "ready", "result": stored_result}
    return {"status": "waiting"}
