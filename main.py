"""
Quantitative Backtesting & Portfolio Optimization Engine
=========================================================
Single entry point. Runs the full pipeline end-to-end:

    1. Fetch & cache price data
    2. Run backtests (Equal Weight, Half-Kelly, Full Kelly)
    3. Walk-forward out-of-sample validation  [if WALK_FORWARD=True]
    4. Run Monte Carlo simulation
    5. Generate all charts
    6. Generate and save text report

Usage:
    source venv/bin/activate && python main.py
"""

import logging
from pathlib import Path

import numpy as np

import config
from src.data.fetcher import fetch_prices
from src.engine.backtest import run_backtest
from src.monte_carlo.simulation import run_monte_carlo
from src.optimization.equal_weight import equal_weight_signal
from src.optimization.signals import make_kelly_signal
from src.validation.oos_metrics import compare_is_oos
from src.validation.walk_forward import WalkForwardConfig, run_walk_forward
from src.visualization.charts import (
    plot_drawdowns,
    plot_equity_curves,
    plot_is_vs_oos_equity,
    plot_monthly_heatmap,
    plot_monte_carlo_fan,
    plot_rolling_sharpe,
    plot_weight_evolution,
)
from src.visualization.report import generate_report

# Set to False to skip walk-forward validation (faster pipeline for quick runs)
WALK_FORWARD = True

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    logger.info("=" * 62)
    logger.info("  Quant Backtest Engine — Full Pipeline")
    logger.info("=" * 62)

    # ── 1. Data ──────────────────────────────────────────────────
    logger.info("[1/6] Fetching price data...")
    prices = fetch_prices()
    logger.info("      %d assets × %d trading days", len(prices.columns), len(prices))

    # ── 2. Backtests ─────────────────────────────────────────────
    logger.info("[2/6] Running backtests...")

    half_kelly_signal = make_kelly_signal(fraction=0.5, cov_method="ledoit_wolf")
    full_kelly_signal = make_kelly_signal(fraction=1.0, cov_method="ledoit_wolf")

    ew_result     = run_backtest(prices, equal_weight_signal, rebalance_freq="monthly")
    hk_result     = run_backtest(prices, half_kelly_signal,   rebalance_freq="monthly")
    fk_result     = run_backtest(prices, full_kelly_signal,   rebalance_freq="monthly")

    backtest_results = {
        "Equal Weight": ew_result,
        "Half-Kelly":   hk_result,
        "Full Kelly":   fk_result,
    }

    logger.info("      Equal Weight  — CAGR %.1f%%  Sharpe N/A (see report)",
                ew_result.cagr * 100)
    logger.info("      Half-Kelly    — CAGR %.1f%%", hk_result.cagr * 100)
    logger.info("      Full Kelly    — CAGR %.1f%%", fk_result.cagr * 100)

    # ── 3. Walk-Forward Validation ───────────────────────────────
    wf_result = None
    if WALK_FORWARD:
        logger.info("[3/6] Walk-forward out-of-sample validation...")
        wf_result = run_walk_forward(
            prices,
            wf_config=WalkForwardConfig(),
            in_sample_result=hk_result,   # reuse already-computed IS result
        )
        logger.info(
            "      OOS start: %s | IS Sharpe %.3f | OOS Sharpe %.3f",
            wf_result.oos_start_date.date(),
            wf_result.in_sample_metrics.sharpe_ratio,
            wf_result.oos_metrics.sharpe_ratio,
        )
        compare_is_oos(wf_result.in_sample_metrics, wf_result.oos_metrics)

    # ── 4. Monte Carlo ───────────────────────────────────────────
    logger.info("[4/6] Running Monte Carlo (%d paths × %d days)...",
                config.MC_NUM_PATHS, config.MC_HORIZON_DAYS)
    mc_result = run_monte_carlo(
        daily_returns=hk_result.daily_returns,
        n_paths=config.MC_NUM_PATHS,
        n_days=config.MC_HORIZON_DAYS,
        initial_capital=config.INITIAL_CAPITAL,
        seed=config.MC_SEED,
        store_paths=True,
    )
    logger.info("      P(profit)=%.1f%%  Median terminal $%s",
                mc_result.prob_profit * 100,
                f"{mc_result.median_terminal_wealth:,.0f}")

    # ── 5. Charts ────────────────────────────────────────────────
    logger.info("[5/6] Generating charts → %s", config.CHART_DIR)
    Path(config.CHART_DIR).mkdir(parents=True, exist_ok=True)

    equity_map = {name: r.equity_curve for name, r in backtest_results.items()}
    returns_map = {name: r.daily_returns for name, r in backtest_results.items()}

    saved = []

    p = plot_equity_curves(equity_map)
    saved.append(p)
    logger.info("      + %s", p.name)

    p = plot_monte_carlo_fan(mc_result.equity_paths, config.INITIAL_CAPITAL)
    saved.append(p)
    logger.info("      + %s", p.name)

    p = plot_rolling_sharpe(returns_map)
    saved.append(p)
    logger.info("      + %s", p.name)

    p = plot_drawdowns(equity_map)
    saved.append(p)
    logger.info("      + %s", p.name)

    p = plot_monthly_heatmap(hk_result.daily_returns, strategy_name="Half-Kelly")
    saved.append(p)
    logger.info("      + %s", p.name)

    p = plot_weight_evolution(hk_result.positions, strategy_name="Half-Kelly")
    saved.append(p)
    logger.info("      + %s", p.name)

    if wf_result is not None:
        p = plot_is_vs_oos_equity(
            wf_result.in_sample_result.equity_curve,
            wf_result.oos_result.equity_curve,
            oos_start_date=wf_result.oos_start_date,
        )
        saved.append(p)
        logger.info("      + %s", p.name)

    logger.info("      %d charts saved.", len(saved))

    # ── 6. Report ────────────────────────────────────────────────
    logger.info("[6/6] Generating report → %s", config.REPORT_PATH)
    generate_report(backtest_results, kelly_result=hk_result)

    # ── Done ─────────────────────────────────────────────────────
    logger.info("Pipeline complete.")
    logger.info("      Charts: %s", config.CHART_DIR)
    logger.info("      Report: %s", config.REPORT_PATH)


if __name__ == "__main__":
    main()
