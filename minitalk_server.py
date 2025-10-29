# from fastapi import FastAPI, Request
# from fastapi.middleware.cors import CORSMiddleware

# app = FastAPI()
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # -------------------------------
# # Storage
# # -------------------------------
# stored_weights = []  # clients' local models
# global_weights = None


# @app.post("/send_weights")
# async def receive_weights(req: Request):
#     """Receive local model weights from clients"""
#     global stored_weights
#     data = await req.json()
#     weights = data.get("weights")
#     if weights:
#         stored_weights.append(weights)
#         print(f"📥 Received client weights: {weights}")
#         return {"status": "weights_received", "count": len(stored_weights)}
#     return {"status": "error", "msg": "no weights"}


# @app.get("/fetch_weights")
# async def send_weights():
#     """Send all stored client weights to server aggregator"""
#     global stored_weights
#     if stored_weights:
#         print(f"📤 Sending {len(stored_weights)} client weights to server aggregator")
#         return {"status": "ready", "weights": stored_weights}
#     return {"status": "waiting"}


# @app.post("/send_global")
# async def receive_global(req: Request):
#     """Receive global aggregated weights from server"""
#     global global_weights, stored_weights
#     data = await req.json()
#     global_weights = data.get("global_weights")
#     print(f"✅ Received global weights from aggregator: {global_weights}")

#     # clear old client weights for next round
#     stored_weights = []
#     return {"status": "global_stored"}


# @app.get("/fetch_global")
# async def send_global():
#     """Send global model weights back to clients"""
#     global global_weights
#     if global_weights:
#         print(f"📤 Sending global weights to clients: {global_weights}")
#         return {"status": "ready", "global_weights": global_weights}
#     return {"status": "waiting"}





# from fastapi import FastAPI, Request
# from fastapi.middleware.cors import CORSMiddleware

# app = FastAPI()

# # CORS for frontend / remote access
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # -----------------------------
# # Global State
# # -----------------------------
# EXPECTED_CLIENTS = 2          # 🔹 Number of clients
# TOTAL_ROUNDS = 3              # 🔹 Number of rounds
# current_round = 0
# stored_weights = {}           # client_id -> weights
# global_weights = None
# logs = []                     # store round metrics


# -----------------------------
# API Endpoints
# -----------------------------
# @app.get("/")
# def home():
#     return {"status": "FLTalk Mini v2 running!"}


# @app.post("/send_weights")
# async def receive_weights(req: Request):
#     global stored_weights
#     data = await req.json()
#     cid = data.get("client_id")
#     weights = data.get("weights")
#     stored_weights[cid] = weights
#     print(f"📥 Received weights from {cid}")
#     return {"status": "ok", "received_from": cid, "count": len(stored_weights)}


# @app.get("/fetch_weights")
# def fetch_weights():
#     if len(stored_weights) >= EXPECTED_CLIENTS:
#         print("✅ All client weights ready for aggregation")
#         return {"status": "ready", "weights": list(stored_weights.values())}
#     else:
#         return {"status": "waiting", "received": len(stored_weights)}


# @app.post("/send_global")
# async def receive_global(req: Request):
#     global global_weights, stored_weights, current_round, logs
#     data = await req.json()
#     global_weights = data.get("global_weights")
#     metrics = data.get("metrics", {})
#     current_round += 1
#     logs.append({"round": current_round, "metrics": metrics})
#     print(f"✅ Round {current_round} complete. Metrics: {metrics}")
#     stored_weights = {}  # clear for next round
#     return {"status": "round_done", "round": current_round, "metrics": metrics}


# @app.get("/fetch_global")
# def fetch_global():
#     if global_weights is not None:
#         return {"status": "ready", "global_weights": global_weights}
#     else:
#         return {"status": "waiting"}


# @app.get("/get_logs")
# def get_logs():
#     return {"total_rounds": len(logs), "logs": logs}




import sys, os
# ensure algorithms folder is visible (for Render deployment)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '')))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import importlib

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
stored_weights = []   # clients' local models
global_weights = None
ALGORITHM = "fedavg"  # default; can later be made configurable

# -------------------------------
# API Endpoints
# -------------------------------

@app.post("/send_weights")
async def receive_weights(req: Request):
    """Receive local model weights from clients"""
    global stored_weights
    data = await req.json()
    weights = data.get("weights")
    if weights:
        stored_weights.append(weights)
        print(f"✅ Received client weights: {weights}")
        return {"status": "weights_received", "count": len(stored_weights)}
    return {"status": "error", "msg": "no weights"}


@app.get("/fetch_weights")
async def send_weights():
    """Send all stored client weights to server aggregator"""
    global stored_weights
    if stored_weights:
        print(f"📤 Sending {len(stored_weights)} client weights to aggregator")
        return {"status": "ready", "weights": stored_weights}
    return {"status": "waiting"}


@app.post("/send_global")
async def receive_global(req: Request):
    """Receive global aggregated weights from server"""
    global global_weights, stored_weights
    data = await req.json()
    global_weights = data.get("global_weights")
    print(f"🌍 Received global weights: {global_weights}")

    # clear old client weights for next round
    stored_weights = []
    return {"status": "global_stored"}


@app.get("/fetch_global")
async def send_global():
    """Send global model weights back to clients"""
    global global_weights
    if global_weights:
        print(f"📦 Sending global weights to clients: {global_weights}")
        return {"status": "ready", "global_weights": global_weights}
    return {"status": "waiting"}


# -------------------------------
# Algorithm Loader (for testing)
# -------------------------------
@app.get("/test_algorithm/{algo_name}")
async def test_algo(algo_name: str):
    """Optional endpoint to test algorithm import dynamically"""
    try:
        algo_module = importlib.import_module(f"algorithms.{algo_name.lower()}")
        if hasattr(algo_module, "aggregate"):
            return {"status": "success", "algo_found": True}
        else:
            return {"status": "error", "msg": "aggregate() missing"}
    except Exception as e:
        return {"status": "error", "msg": str(e)}
