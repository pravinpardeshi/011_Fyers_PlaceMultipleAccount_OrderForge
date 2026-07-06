import threading
from fyers_apiv3 import fyersModel

class FyersAccount:
    """Represents an individual Fyers trading account session."""
    
    def __init__(self, name: str, client_id: str, access_token: str):
        self.name = name
        self.client_id = client_id
        self.access_token = access_token
        self.client = None

    def connect(self) -> bool:
        """Establishes the API connection session."""
        try:
            self.client = fyersModel.FyersModel(
                client_id=self.client_id,
                token=self.access_token,
                is_async=False,
                log_path=""
            )
            print(f"[✓] Connection successful for {self.name}")
            return True
        except Exception as e:
            print(f"[✗] Connection failed for {self.name}: {e}")
            return False

    def execute_order(self, order_payload: dict):
        """Sends a single order payload to the Fyers gateway."""
        if not self.client:
            print(f"[{self.name}] Error: Session not initialized.")
            return

        try:
            print(f"[{self.name}] Sending order...")
            response = self.client.place_order(data=order_payload)
            print(f"[{self.name}] Response: {response}")
        except Exception as e:
            print(f"[{self.name}] Order failed: {e}")


class OrderManager:
    """Manages multi-account orchestration and parallel execution."""
    
    def __init__(self):
        self.accounts = []

    def register_account(self, account: FyersAccount):
        """Adds a new FyersAccount to the tracking list."""
        if account.connect():
            self.accounts.append(account)

    def broadcast_order(self, order_payload: dict):
        """Dispatches the order to all registered accounts concurrently using threads."""
        if not self.accounts:
            print("[!] Broadcast aborted: No active accounts registered.")
            return

        threads = []
        
        # Instantiate and start a separate thread for each account object
        for account in self.accounts:
            t = threading.Thread(
                target=account.execute_order, 
                args=(order_payload,)
            )
            threads.append(t)
            t.start()

        # Synchronize threads
        for t in threads:
            t.join()


# --- Execution Execution ---
if __name__ == "__main__":
    
    # 1. Initialize the manager instance
    manager = OrderManager()

    # 2. Instantiate and register Account 1
    account_1 = FyersAccount(
        name="Primary_Account",
        client_id="L9XXXXXX-100",
        access_token="eyJhbGciOiJIUzI1Ni..."
    )
    manager.register_account(account_1)

    # 3. Instantiate and register Account 2
    account_2 = FyersAccount(
        name="Secondary_Account",
        client_id="XWXXXXXX-100",
        access_token="eyJhbGciOiJIUzI1Ni..."
    )
    manager.register_account(account_2)

    # 4. Standard Order Blueprint
    shared_order = {
        "symbol": "NSE:SBIN-EQ",
        "qty": 1,
        "type": 2,                  # 2 = Market Order
        "side": 1,                  # 1 = Buy
        "productType": "INTRADAY",
        "limitPrice": 0,
        "stopPrice": 0,
        "validity": "DAY",
        "disclosedQty": 0,
        "offlineOrder": False,
        "stopLoss": 0,
        "takeProfit": 0
    }

    # 5. Execute parallel trade across all active instances
    print("\n--- Initiating Multi-Account OOP Order Dispatch ---")
    manager.broadcast_order(shared_order)
    print("--- Dispatch Cycle Complete ---")


