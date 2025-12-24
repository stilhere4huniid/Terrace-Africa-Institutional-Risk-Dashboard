import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import time
from fpdf import FPDF
import os
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Terrace Africa Risk Dashboard", 
    layout="wide",
    page_icon="🏦"
)

# --- 1. ENTERPRISE DATA HANDLERS ---

def initialize_demo_data():
    """
    Creates a calibrated CSV (v5) matching the Project 2 Report exactly.
    """
    if not os.path.exists('portfolio_data_v5.csv'):
        data = {
            'Asset Name': [
                'Greenfields Retail (Zim)', 'Zimre Park Drive-Thru (Zim)', 
                'Highland Park & Others (Zim)', 'Waterfalls Mall (Zambia)', 
                'Mozambique Portfolio (Tete)', 'RSA Portfolio (Kleinmond)'
            ],
            'Value ($M)': [24.2, 0.89, 32.91, 25.0, 22.0, 15.0],
            'Region': ['Zim', 'Zim', 'Zim', 'Regional', 'Regional', 'Regional'],
            # EXACT PARAMETERS from the Original Notebook
            'Base Volatility': [0.12, 0.10, 0.14, 0.16, 0.20, 0.09], 
            'Expected Return': [0.092, 0.0774, 0.085, 0.11, 0.13, 0.075] 
        }
        df = pd.DataFrame(data)
        df.to_csv('portfolio_data_v5.csv', index=False)
        return True
    return False

def load_portfolio_data():
    """Loads the v5 data file."""
    initialize_demo_data()
    return pd.read_csv('portfolio_data_v5.csv')

def log_simulation(inputs, results):
    """Saves run details for audit."""
    log_entry = {
        'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'User': 'Risk_Manager_01', 
        'Scenario': results['active_scenario'],
        'Confidence': inputs['conf'],
        'Total VaR ($M)': results['total_var'] / 1e6,
        'Risk Ratio': results['total_var'] / results['total_val'],
        'Input_Vol_Zim': inputs['vol_zim'],
        'Input_Shock_Zim': inputs['shock_zim'],
        'Liquidity_Penalty': inputs.get('liq_pen', 0)
    }
    
    log_df = pd.DataFrame([log_entry])
    
    if not os.path.exists('risk_audit_log.csv'):
        log_df.to_csv('risk_audit_log.csv', index=False)
    else:
        log_df.to_csv('risk_audit_log.csv', mode='a', header=False, index=False)

# --- PDF REPORT ENGINE ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.set_text_color(34, 139, 34) # Terrace Green
        self.cell(0, 10, 'TERRACE AFRICA | RISK MANAGEMENT DIVISION', 0, 1, 'L')
        self.line(10, 20, 200, 20)
        self.ln(15)

    def footer(self):
        self.set_y(-25)
        self.set_font('Arial', 'I', 7)
        self.set_text_color(100, 100, 100)
        disclaimer = (
            "DISCLAIMER: For internal use only. Past performance does not guarantee future results. "
            "This report is generated for simulation purposes and does not constitute financial advice. "
            "Terrace Africa Risk Management Division."
        )
        self.multi_cell(0, 4, disclaimer, 0, 'C')
        self.ln(2)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()} | Generated via Institutional Risk Dashboard', 0, 0, 'C')

    def section_title(self, label):
        self.set_font('Arial', 'B', 12)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, label, 0, 1, 'L')
        self.ln(2)

    def body_text(self, text):
        self.set_font('Arial', '', 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 6, text)
        self.ln(5)

    def metric_row(self, label, value):
        self.set_font('Arial', 'B', 10)
        self.cell(60, 8, label, 1)
        self.set_font('Arial', '', 10)
        self.cell(0, 8, value, 1, 1)

def generate_pdf_report(data, inputs):
    pdf = PDF()
    pdf.add_page()
    
    # 1. TITLE
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Portfolio Stress Test Report', 0, 1, 'C')
    pdf.set_font('Arial', 'I', 10)
    pdf.cell(0, 10, f"Scenario: {data['active_scenario']} | Confidence: {inputs['conf']:.0%}", 0, 1, 'C')
    pdf.ln(5)

    # 2. EXECUTIVE SUMMARY
    pdf.section_title("1. Executive Summary & Strategic Interpretation")
    risk_ratio = abs(data['total_var']) / data['total_val']
    
    if risk_ratio < 0.05:
        risk_comment = "The portfolio shows strong resilience. Capital reserves are likely sufficient."
    elif risk_ratio < 0.15:
        risk_comment = "Moderate risk detected. Monitoring of regional volatility is recommended."
    else:
        risk_comment = "CRITICAL ALERT: High capital exposure detected. Immediate liquidity stress testing required."
    
    div_status = "Providing a hedge" if inputs['vol_regional'] < inputs['vol_zim'] else "Amplifying volatility"

    summary = (
        f"This report details the results of a Monte Carlo simulation (10,000 iterations) on the Terrace Africa "
        f"${data['total_val']/1e6:.1f}M Group Portfolio. Under the current parameters, the Group Value-at-Risk (VaR) is "
        f"${abs(data['total_var'])/1e6:.2f} Million.\n\n"
        f"**Strategic Insight:** {risk_comment} "
        f"The regional diversification strategy is currently {div_status} relative to the Zimbabwe core portfolio."
    )
    pdf.body_text(summary)

    # 3. PARAMETERS
    pdf.section_title("2. Stress Test Parameters")
    pdf.set_fill_color(240, 240, 240)
    pdf.metric_row("Zimbabwe Volatility Input", f"{inputs['vol_zim']:.1%}")
    pdf.metric_row("Regional Volatility Input", f"{inputs['vol_regional']:.1%}")
    pdf.metric_row("Zimbabwe Asset Shock", f"{inputs['shock_zim']:.1%}")
    pdf.metric_row("Regional Asset Shock", f"{inputs['shock_reg']:.1%}")
    pdf.metric_row("Liquidity / Fire-Sale Disc.", f"{inputs.get('liq_pen', 0):.1%}")
    pdf.ln(5)

    # 4. METRICS
    pdf.section_title("3. Key Financial Risk Metrics")
    pdf.metric_row("Total Portfolio Value (Post-Shock)", f"${data['total_val']/1e6:.2f} Million")
    pdf.metric_row("Value at Risk (VaR)", f"${abs(data['total_var'])/1e6:.2f} Million")
    pdf.metric_row("Risk-to-Value Ratio", f"{risk_ratio:.2%}")
    pdf.ln(5)

    # 5. ASSETS
    pdf.section_title("4. Asset-Level Vulnerability Ledger")
    pdf.set_font('Arial', 'B', 9)
    pdf.set_fill_color(50, 150, 50) 
    pdf.set_text_color(255, 255, 255)
    pdf.cell(70, 8, "Asset Name", 1, 0, 'L', 1)
    pdf.cell(40, 8, "Adj. Value ($M)", 1, 0, 'C', 1)
    pdf.cell(40, 8, "VaR ($M)", 1, 0, 'C', 1)
    pdf.cell(40, 8, "Risk %", 1, 1, 'C', 1)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 9)
    for index, row in data['df'].iterrows():
        if row['Risk %'] > 0.20: 
            pdf.set_fill_color(255, 230, 230)
        else:
            pdf.set_fill_color(255, 255, 255)
        pdf.cell(70, 8, row['Asset'], 1, 0, 'L', 1)
        pdf.cell(40, 8, f"${row['Adjusted Value ($M)']:.2f}", 1, 0, 'C', 1)
        pdf.cell(40, 8, f"${row['VaR ($M)']:.2f}", 1, 0, 'C', 1)
        pdf.cell(40, 8, f"{row['Risk %']:.2%}", 1, 1, 'C', 1)

    pdf.ln(10)
    pdf.set_font('Arial', 'I', 8)
    pdf.cell(0, 10, "*** End of Risk Report ***", 0, 1, 'C')
    
    return pdf.output(dest='S').encode('latin-1')

# --- MAIN APP LOGIC START ---
st.title("🏦 Terrace Africa | Institutional Risk Dashboard")

# 4. LOAD EXTERNAL DATA & CALCULATE BENCHMARKS
try:
    df_portfolio = load_portfolio_data()
    total_aum = df_portfolio['Value ($M)'].sum()
    
    # Calculate Benchmarks (Weighted Averages)
    zim_assets = df_portfolio[df_portfolio['Region'] == 'Zim']
    reg_assets = df_portfolio[df_portfolio['Region'] != 'Zim']
    bench_vol_zim = (zim_assets['Value ($M)'] * zim_assets['Base Volatility']).sum() / zim_assets['Value ($M)'].sum()
    bench_vol_reg = (reg_assets['Value ($M)'] * reg_assets['Base Volatility']).sum() / reg_assets['Value ($M)'].sum()

    st.markdown(f"**Total AUM: ${total_aum:.1f} Million** | Data Source: `portfolio_data_v5.csv` (External)", 
                help="This data is loaded from a CSV file (v5). It contains the base valuations, volatilities, and expected returns for the 6 core assets as per the Project 2 Report.")

except Exception as e:
    st.error(f"Error loading portfolio data: {e}")
    st.stop()

# --- SIDEBAR & INPUTS ---

# 1. Initialize Defaults to Benchmarks
if 'vol_zim' not in st.session_state: st.session_state['vol_zim'] = int(bench_vol_zim * 100)
if 'vol_regional' not in st.session_state: st.session_state['vol_regional'] = int(bench_vol_reg * 100)
if 'shock_zim' not in st.session_state: st.session_state['shock_zim'] = 0
if 'shock_reg' not in st.session_state: st.session_state['shock_reg'] = 0
if 'liq_pen' not in st.session_state: st.session_state['liq_pen'] = 10 
if 'conf' not in st.session_state: st.session_state['conf'] = 0.95

# 2. Reset Button (WITH TOOLTIP)
if st.sidebar.button("🔄 Reset to Benchmarks", help="Click to restore all sliders to the market-weighted averages and clear any custom stress scenarios. Returns the model to the $1.66M VaR baseline."):
    st.session_state['vol_zim'] = int(bench_vol_zim * 100)
    st.session_state['vol_regional'] = int(bench_vol_reg * 100)
    st.session_state['shock_zim'] = 0
    st.session_state['shock_reg'] = 0
    st.session_state['liq_pen'] = 10 
    st.session_state['conf'] = 0.95
    if 'data' in st.session_state: del st.session_state['data']
    st.rerun()

# 3. Form (WITH TOOLTIPS EVERYWHERE)
with st.sidebar.form(key="stress_test_form"):
    st.header("📉 Stress Test Scenarios")
    
    vol_zim = st.slider(
        "Zimbabwe Volatility (%)", 10, 50, key="vol_zim",
        help="Adjust the uncertainty of Zimbabwe assets. Higher % = Wider range of potential outcomes. Default is the weighted average of Zim assets."
    ) / 100
    st.caption(f"📊 Market Benchmark: {bench_vol_zim:.1%}", help="The actual weighted average volatility of your Zimbabwe portfolio (12.7%).")
    
    vol_regional = st.slider(
        "Regional Volatility (%)", 10, 50, key="vol_regional",
        help="Adjust the uncertainty for assets in Zambia, Mozambique, and RSA. Default is the weighted average of Regional assets."
    ) / 100
    st.caption(f"📊 Market Benchmark: {bench_vol_reg:.1%}", help="The actual weighted average volatility of your Regional portfolio (15.7%).")
    
    st.markdown("---")
    shock_zim = st.slider(
        "Zim Asset Shock (%)", -50, 20, key="shock_zim",
        help="Simulate an immediate crash (e.g. -20%) or boom (+10%) in Zimbabwe property values."
    ) / 100
    
    shock_regional = st.slider(
        "Regional Asset Shock (%)", -50, 20, key="shock_reg",
        help="Simulate an immediate crash or boom in Regional property values (e.g. Market Contagion)."
    ) / 100
    
    liquidity_pen = st.slider(
        "Liquidity / Fire-Sale Discount (%)", 0, 30, key="liq_pen",
        help="Applies a penalty to asset value ONLY if a negative shock occurs. Simulates the loss from selling illiquid real estate quickly during a crisis."
    ) / 100
    
    st.markdown("---")
    confidence = st.selectbox(
        "Confidence Level", [0.90, 0.95, 0.99], key="conf",
        help="95% Confidence means there is a 95% chance losses will not exceed the VaR figure. 99% is a stricter test for extreme tail risks."
    )
    run_btn = st.form_submit_button("🚀 Run Simulation", type="primary", help="Click to run 10,000 Monte Carlo simulations using these parameters.")

# FUNCTION: Run Simulation
def run_simulation():
    inputs = {
        'vol_zim': vol_zim, 'vol_regional': vol_regional,
        'shock_zim': shock_zim, 'shock_reg': shock_regional,
        'liq_pen': liquidity_pen,
        'conf': confidence
    }
    
    np.random.seed(50) # SEED 50 REPLICATES PROJECT 2 EXACTLY
    simulations = 10000 # MATCHES PROJECT 2 SIMULATION COUNT
    results = []
    total_pnl = np.zeros(simulations)

    # Detect if user is running "Base Case" (Sliders match Benchmarks)
    is_zim_base = abs(vol_zim - bench_vol_zim) < 0.02
    is_reg_base = abs(vol_regional - bench_vol_reg) < 0.02

    for index, row in df_portfolio.iterrows():
        name = row['Asset Name']
        val = row['Value ($M)']
        region = row['Region']
        base_vol = row['Base Volatility']
        base_return = row['Expected Return'] 
        
        # LOGIC: GRANULAR VS OVERRIDE
        if region == 'Zim':
            shock = shock_zim
            vol = base_vol if is_zim_base else vol_zim 
        else:
            shock = shock_regional
            vol = base_vol if is_reg_base else vol_regional

        if shock < 0:
            applied_liq_discount = liquidity_pen
        else:
            applied_liq_discount = 0
            
        current_val = val * (1 + shock) * (1 - applied_liq_discount) * 1_000_000
        
        # Monte Carlo with SPECIFIC RETURN
        drift = base_return - 0.5 * vol ** 2 
        shocks = np.random.normal(0, 1, simulations)
        rets = np.exp(drift + vol * shocks)
        future_vals = current_val * rets
        pnl = future_vals - current_val
        total_pnl += pnl
        
        var = np.percentile(pnl, (1 - confidence) * 100)
        results.append({
            "Asset": name,
            "Adjusted Value ($M)": current_val / 1e6,
            "VaR ($M)": abs(var) / 1e6,
            "Risk %": abs(var) / current_val,
            "Shock Applied": f"{shock:.0%}"
        })

    total_var = np.percentile(total_pnl, (1 - confidence) * 100)
    total_val_post_shock = sum(x['Adjusted Value ($M)'] for x in results) * 1_000_000
    
    data_pack = {
        'active_scenario': "Stress Test" if (shock_zim < 0 or shock_regional < 0) else "Base Case",
        'total_var': total_var,
        'total_val': total_val_post_shock,
        'df': pd.DataFrame(results),
        'total_pnl': total_pnl,
        'inputs': inputs
    }
    
    st.session_state.data = data_pack
    log_simulation(inputs, data_pack)

# --- CONTROL FLOW ---
if run_btn:
    with st.spinner('Running 10,000 Monte Carlo Simulations...'):
        time.sleep(0.5)
        run_simulation()

if 'data' not in st.session_state:
    run_simulation()

# --- RENDER DASHBOARD ---
if 'data' in st.session_state:
    data = st.session_state.data
    inputs = data['inputs']
    df_res = data['df']
    
    base_val_approx = df_portfolio['Value ($M)'].sum()
    impact_val = (data['total_val']/1e6) - base_val_approx

    # Metrics (WITH TOOLTIPS)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Projected Portfolio Value", f"${data['total_val']/1e6:.2f} M", delta=f"{impact_val:.2f} M Impact", help="The total estimated value of the portfolio after applying any asset shocks and liquidity discounts.")
    col2.metric(f"Group VaR ({inputs['conf']:.0%})", f"${abs(data['total_var'])/1e6:.2f} M", delta="- Downside Risk", delta_color="inverse", help=f"Value at Risk: There is a {inputs['conf']:.0%} probability that losses will NOT exceed this amount over the next year.")
    col3.metric("Active Scenario", data['active_scenario'], help="Shows if the current simulation is a 'Base Case' (using benchmark volatility) or a 'Stress Test' (using your custom slider inputs).")

    with col4:
        st.write("") 
        pdf_bytes = generate_pdf_report(data, inputs)
        st.download_button(
            label="📄 Download PDF Report", 
            data=pdf_bytes, 
            file_name="Terrace_Africa_Risk_Report.pdf", 
            mime="application/pdf", 
            type="primary",
            help="Generate a professional PDF report summarizing these results for the board."
        )

    # Charts
    col_left, col_right = st.columns([2, 1])
    with col_left:
        st.subheader("⚠️ Tail Risk Distribution", help="This histogram displays the spread of 10,000 potential outcomes. The red dotted line marks the VaR threshold—the 'Danger Zone'.")
        fig_hist = px.histogram(data['total_pnl']/1e6, nbins=50, title="PnL Distribution ($M)", color_discrete_sequence=['#2E8B57'])
        fig_hist.add_vline(x=data['total_var']/1e6, line_width=3, line_dash="dash", line_color="red")
        fig_hist.update_layout(showlegend=False, xaxis_title="Profit / Loss ($M)")
        st.plotly_chart(fig_hist, use_container_width=True)

    with col_right:
        st.subheader("Risk Contribution", help="Which specific asset is contributing the most to the total portfolio risk? Larger slices mean higher risk.")
        fig_pie = px.pie(df_res, values='VaR ($M)', names='Asset', hole=0.4, color_discrete_sequence=px.colors.sequential.Greens_r)
        st.plotly_chart(fig_pie, use_container_width=True)

    # Ledger & Heatmap
    st.markdown("---")
    st.subheader("Detailed Risk Ledger", help="A breakdown of Value at Risk for each individual asset.")
    st.dataframe(df_res.style.format({"Adjusted Value ($M)": "${:.2f}", "VaR ($M)": "${:.2f}", "Risk %": "{:.2%}"}).background_gradient(subset=['Risk %'], cmap='Reds'), use_container_width=True)

    st.markdown("---")
    st.subheader("Risk Heatmap (Asset Vulnerability)", help="Visualizes risk intensity. RED = High Risk %. SIZE = Dollar Value at Risk.")
    fig_heat = px.scatter(df_res, x="Adjusted Value ($M)", y="Risk %", size="VaR ($M)", color="Risk %", text="Asset", size_max=60, color_continuous_scale="Reds", title="Interactive Risk Map: Bubble Size = VaR ($)")
    
    # FIXED: Added cliponaxis=False to allow labels to spill outside the chart area
    fig_heat.update_traces(textposition='top center', cliponaxis=False, textfont=dict(size=12, color='black'), marker=dict(line=dict(width=1, color='DarkSlateGrey')))
    
    fig_heat.update_layout(height=600, margin=dict(t=50, l=50, r=50, b=50), yaxis=dict(title="Risk %", tickformat=".1%"), xaxis=dict(title="Asset Value ($M)"), showlegend=False)
    st.plotly_chart(fig_heat, use_container_width=True)