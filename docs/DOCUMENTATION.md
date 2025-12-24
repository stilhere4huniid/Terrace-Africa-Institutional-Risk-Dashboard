# 📘 Technical Documentation

## Code Structure (`dashboard.py`)

### 1. Data Layer
* `initialize_demo_data()`: Generates a CSV file (`portfolio_data_final.csv`) containing the calibrated asset valuations, volatilities, and expected returns.
* `load_portfolio_data()`: Loads the CSV into a Pandas DataFrame. It includes a self-healing mechanism that regenerates the file if the schema is incorrect or missing.

### 2. Simulation Engine
* `run_simulation()`: The core function.
    * **Inputs:** Volatility sliders, Shock sliders, Confidence level.
    * **Logic:** Applies shocks -> Applies Liquidity Penalty -> Runs 10,000 Monte Carlo paths -> Calculates PnL.
    * **Output:** Updates `st.session_state` with results and logs the run to `risk_audit_log.csv`.

### 3. Reporting Engine
* `class PDF(FPDF)`: A custom class inheriting from `fpdf`. Defines the corporate header and footer with disclaimers.
* `generate_pdf_report()`: Compiles simulation results into a 2-page PDF, including Executive Summary, Parameters, and Asset Ledger.