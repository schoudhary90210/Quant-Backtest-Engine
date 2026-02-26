"""Shared pytest fixtures for the test suite."""

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def sample_prices() -> pd.DataFrame:
    """Generate synthetic price data for 3 assets over 252 trading days."""
    np.random.seed(42)
    dates = pd.bdate_range("2020-01-01", periods=252)
    tickers = ["AAA", "BBB", "CCC"]
    data = {}
    for ticker in tickers:
        # Geometric Brownian Motion: drift=0.05/252, vol=0.20/sqrt(252)
        daily_returns = np.random.normal(0.05 / 252, 0.20 / np.sqrt(252), 252)
        prices = 100.0 * np.exp(np.cumsum(daily_returns))
        data[ticker] = prices
    return pd.DataFrame(data, index=dates)


@pytest.fixture
def sample_log_returns(sample_prices: pd.DataFrame) -> pd.DataFrame:
    """Log returns derived from sample_prices."""
    return np.log(sample_prices / sample_prices.shift(1)).dropna()
