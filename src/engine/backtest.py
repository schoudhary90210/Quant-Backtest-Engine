"""
Event-driven backtester core loop.

Daily rebalance cycle: generate signals → calculate target weights →
apply transaction costs and slippage → update portfolio state → log metrics.
Tracks equity curve, daily returns, positions, and turnover.
"""
