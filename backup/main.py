from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import threading
from fyers_apiv3 import fyersModel

app = FastAPI(title="Fyers Multi-Account Trade Terminal")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Hardcoded Account Credentials (Generate Access Tokens Daily)
# In production, migrate these to secure environment variables or a database.
ACCOUNTS_CONFIG = {
    "Primary_Account": {
        "client_id": "L9XXXXXX-100",
        "access_token": "eyJhbGciOiJIUzI1Ni..."
    },
    "Secondary_Account": {
        "client_id": "XWXXXXXX-100",
        "access_token": "eyJhbGciOiJIUzI1Ni..."
    }
}

# Request schema matching Fyers SDK requirements
class OrderRequest(BaseModel):
    symbol: str = Field(..., example="NSE:SBIN-EQ")
    qty: int = Field(..., gt=0, example=1)
    type: int = Field(..., description="1=Limit, 2=Market", example=2)
    side: int = Field(..., description="1=Buy, -1=Sell", example=1)
    productType: str = Field(..., example="INTRADAY")

def initialize_fyers_client(client_id: str, access_token: str):
    """Utility to initialize a safe Fyers SDK Instance"""
    return fyersModel.FyersModel(
        client_id=client_id,
        token=access_token,
        is_async=False,
        log_path=""
    )

def send_order_worker(account_name: str, config: dict, payload: dict, results: dict):
    """Thread worker execution loop to avoid global state pollution."""
    try:
        client = initialize_fyers_client(config["client_id"], config["access_token"])
        
        # Build strict Fyers order object structure
        fyers_payload = {
            "symbol": payload["symbol"],
            "qty": payload["qty"],
            "type": payload["type"],
            "side": payload["side"],
            "productType": payload["productType"],
            "limitPrice": 0,
            "stopPrice": 0,
            "validity": "DAY",
            "disclosedQty": 0,
            "offlineOrder": False,
            "stopLoss": 0,
            "takeProfit": 0
        }
        
        response = client.place_order(data=fyers_payload)
        results[account_name] = {"status": "success", "details": response}
    except Exception as e:
        results[account_name] = {"status": "failed", "error": str(e)}

@app.post("/api/v1/place-order")
async def place_multi_account_order(order: OrderRequest):
    order_dict = order.dict()
    threads = []
    execution_results = {}

    # Parallelize the network I/O block via threading
    for account_name, config in ACCOUNTS_CONFIG.items():
        t = threading.Thread(
            target=send_order_worker,
            args=(account_name, config, order_dict, execution_results)
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    return {
        "message": "Multi-account dispatch execution sequence complete.",
        "results": execution_results
    }

@app.get("/")
def place_multi_account_order(order: OrderRequest):
    return FileResponse('index.html')



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8193, reload=True)


