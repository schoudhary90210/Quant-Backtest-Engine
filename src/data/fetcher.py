"""
Yahoo Finance data ingestion.

Downloads adjusted close prices for the configured asset universe,
caches results as parquet files to avoid redundant API calls.
"""
