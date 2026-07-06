import threading
from fyers_apiv3 import fyersModel

# --- CONFIGURATION AREA ---
# You must generate your daily access token for each account via the 
# standard Fyers OAuth2 / TOTP flow before executing this script.
ACCOUNTS_CONFIG = {
    "Account_1": {
        "client_id": "L9XXXXXX-100",        # App ID for Account 1
        "access_token": "eyJhbGciOiJIUzI1Ni..." # Daily Token for Account 1
    },
    "Account_2": {
        "client_id": "XWXXXXXX-100",        # App ID for Account 2
        "access_token": "eyJhbGciOiJIUzI1Ni..." # Daily Token for Account 2
    }
}

def initialize_sessions(config):
    """Initializes and returns ready-to-use Fyers SDK instances for all accounts."""
    sessions = {}
    for account_name, credentials in config.items():
        try:
            # Initialize the V3 client model
            fyers_instance = fyersModel.FyersModel(
                client_id=credentials["client_id"],
                token=credentials["access_token"],
                is_async=False,
                log_path=""
            )
            sessions[account_name] = fyers_instance
            print(f"[✓] Session initialized successfully for {account_name}")
        except Exception as e:
            print(f"[✗] Failed to initialize session for {account_name}: {e}")
    return sessions

def place_order_worker(account_name, fyers_client, order_data):
    """Worker function executed by threads to fire orders simultaneously."""
    try:
        print(f"[{account_name}] Sending order...")
        response = fyers_client.place_order(data=order_data)
        print(f"[{account_name}] Response: {response}")
    except Exception as e:
        print(f"[{account_name}] Order placement failed: {e}")

def broadcast_order(sessions, shared_order_data):
    """Spawns parallel threads to achieve near-simultaneous order execution across accounts."""
    threads = []
    
    for account_name, fyers_client in sessions.items():
        # Pass a thread-safe execution call
        t = threading.Thread(
            target=place_order_worker, 
            args=(account_name, fyers_client, shared_order_data)
        )
        threads.append(t)
        t.start()

    # Wait for all threads to complete execution
    for t in threads:
        t.join()

if __name__ == "__main__":
    # 1. Boot up both client profiles
    active_sessions = initialize_sessions(ACCOUNTS_CONFIG)
    
    if len(active_sessions) < 2:
        print("[!] Execution halted: Not all sessions initialized correctly.")
        exit(1)

    # 2. Define the unified order parameters (NSE Example)
    # Ref: Type 1 = Limit Order, Type 2 = Market Order
    # Ref: Side 1 = Buy, Side -1 = Sell
    order_payload = {
        "symbol": "NSE:SBIN-EQ",
        "qty": 1,
        "type": 2,                  # 2 = Market Order
        "side": 1,                  # 1 = Buy
        "productType": "INTRADAY",  # INTRADAY, CNC, or MARGIN
        "limitPrice": 0,
        "stopPrice": 0,
        "validity": "DAY",
        "disclosedQty": 0,
        "offlineOrder": False,
        "stopLoss": 0,
        "takeProfit": 0
    }

    # 3. Fire orders concurrently
    print("\n--- Triggering Dual Account Order Execution ---")
    broadcast_order(active_sessions, order_payload)
    print("--- Process Complete ---")

