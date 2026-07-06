"""
Configuration — edit values here directly.
No .env file needed.
"""

# ─── Database ──────────────────────────────────────────────
# SQLite (zero config, no server needed)
DATABASE_URL = "sqlite+aiosqlite:///fyers_orders.db"

# PostgreSQL (uncomment below, comment out SQLite line above)
# DATABASE_URL = "postgresql+asyncpg://postgres:password@localhost:5432/fyers_orders"

# ─── Fyers API ─────────────────────────────────────────────
DEFAULT_REDIRECT_URI = "https://trade.fyers.in/api-login/redirect-uri/index.html"

# ─── Server ────────────────────────────────────────────────
HOST = "0.0.0.0"
PORT = 8000
