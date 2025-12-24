# 📉 Risk Modeling Methodology

## 1. Core Simulation Engine
This project uses a **Monte Carlo Simulation** based on Geometric Brownian Motion (GBM) to forecast the future value of a real estate portfolio over a 1-year horizon.

### Mathematical Model
For each asset $i$, the future value $S_t$ is calculated as:

$$S_t = S_0 \cdot \exp \left( (\mu - \frac{\sigma^2}{2})t + \sigma W_t \right)$$

Where:
* $S_0$: Current Asset Valuation (adjusted for shocks)
* $\mu$: Expected Annual Return (Drift)
* $\sigma$: Annual Volatility (Risk)
* $W_t$: Wiener Process (Random walk component)

## 2. Risk Metrics
* **Value at Risk (VaR):** The maximum expected loss at a 95% (or 99%) confidence level.
* **Expected Shortfall (CVaR):** The average loss in scenarios that exceed the VaR threshold.
* **Diversification Benefit:** The model accounts for imperfect correlations between Zimbabwe and Regional (Zambia/Mozambique/RSA) markets.

## 3. Stress Testing & Liquidity
Unlike standard stock market models, this engine includes specific adjustments for real estate illiquidity:
* **Fire-Sale Discount:** A dynamic penalty applied to asset valuations if a negative shock occurs.
* **Scenario Shocks:** Deterministic shocks (e.g., "Zim Currency Devaluation -20%") applied *before* the stochastic simulation.

## 4. Calibration
* **Simulations:** 10,000 iterations per run.
* **Random Seed:** Fixed at `50` to ensure reproducibility of the baseline VaR ($1.66M).