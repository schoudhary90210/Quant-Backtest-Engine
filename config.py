"""
Central configuration for the backtesting engine.
All tunable parameters live here — no magic numbers in library code.
"""

# ──────────────────────────────────────────────
# Asset Universe
# ──────────────────────────────────────────────
ASSETS = [
    "SPY",      # S&P 500
    "QQQ",      # Nasdaq 100
    "IWM",      # Russell 2000
    "EFA",      # International Developed
    "TLT",      # 20+ Year Treasury
    "IEF",      # 7-10 Year Treasury
    "GLD",      # Gold
    "SLV",      # Silver
    "USO",      # Oil
    "BTC-USD",  # Bitcoin
    "DBA",      # Agriculture
    "VNQ",      # Real Estate (REITs)
]

# ──────────────────────────────────────────────
# Data
# ──────────────────────────────────────────────
START_DATE = "2010-01-01"
END_DATE = "2025-12-31"
CACHE_DIR = "data/cache"

# ──────────────────────────────────────────────
# Backtest Engine
# ──────────────────────────────────────────────
INITIAL_CAPITAL = 1_000_000  # $1M starting portfolio
REBALANCE_FREQ = "monthly"   # 'daily' or 'monthly'
TRANSACTION_COST_BPS = 10    # 10 basis points round-trip
SLIPPAGE_BPS = 5             # 5 basis points slippage

# ──────────────────────────────────────────────
# Optimizer
# ──────────────────────────────────────────────
RISK_FREE_RATE = 0.04        # Annualized
KELLY_FRACTION = 0.5         # Half-Kelly (0.5), Full Kelly (1.0)
MAX_POSITION_WEIGHT = 0.40   # No single asset > 40%
MAX_LEVERAGE = 1.5           # Total gross exposure cap
LOOKBACK_WINDOW = 252        # Trading days for return estimation
COV_METHOD = "ledoit_wolf"   # 'ledoit_wolf', 'sample', 'ewma'
EWMA_LAMBDA = 0.94           # For EWMA covariance

# ──────────────────────────────────────────────
# Monte Carlo
# ──────────────────────────────────────────────
MC_NUM_PATHS = 50_000
MC_HORIZON_DAYS = 252        # 1 year forward simulation
MC_SEED = 42

# ──────────────────────────────────────────────
# Risk
# ──────────────────────────────────────────────
VAR_CONFIDENCE = 0.95
ROLLING_SHARPE_WINDOW = 252
REGIME_VOL_THRESHOLDS = {
    "bull": 0.15,            # < 15% annualized vol
    "sideways": 0.25,        # 15-25%
    # "bear" = everything above 25%
}

# ──────────────────────────────────────────────
# Output
# ──────────────────────────────────────────────
CHART_DIR = "output/charts"
REPORT_PATH = "output/report.txt"
CHART_DPI = 300
