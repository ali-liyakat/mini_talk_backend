from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Storage
# -------------------------------
stored_weights = []  # clients' local models
global_weights = None


@app.post("/send_weights")
async def receive_weights(req: Request):
    """Receive local model weights from clients"""
    global stored_weights
    data = await req.json()
    weights = data.get("weights")
    if weights:
        stored_weights.append(weights)
        print(f"📥 Received client weights: {weights}")
        return {"status": "weights_received", "count": len(stored_weights)}
    return {"status": "error", "msg": "no weights"}


@app.get("/fetch_weights")
async def send_weights():
    """Send all stored client weights to server aggregator"""
    global stored_weights
    if stored_weights:
        print(f"📤 Sending {len(stored_weights)} client weights to server aggregator")
        return {"status": "ready", "weights": stored_weights}
    return {"status": "waiting"}


@app.post("/send_global")
async def receive_global(req: Request):
    """Receive global aggregated weights from server"""
    global global_weights, stored_weights
    data = await req.json()
    global_weights = data.get("global_weights")
    print(f"✅ Received global weights from aggregator: {global_weights}")

    # clear old client weights for next round
    stored_weights = []
    return {"status": "global_stored"}


@app.get("/fetch_global")
async def send_global():
    """Send global model weights back to clients"""
    global global_weights
    if global_weights:
        print(f"📤 Sending global weights to clients: {global_weights}")
        return {"status": "ready", "global_weights": global_weights}
    return {"status": "waiting"}
