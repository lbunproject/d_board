import streamlit as st
import requests
import json
import base64

# Set page configuration
st.set_page_config(page_title="WESO Dashboard", layout="wide")

# Function to fetch WESO contract balance for a specific address
def fetch_weso_balance(address):
    query_data = {
        "balance": {"address": address}
    }
    query_data_encoded = base64.b64encode(json.dumps(query_data).encode()).decode()
    url = f"https://terra-classic-lcd.publicnode.com/cosmwasm/wasm/v1/contract/terra13ryrrlcskwa05cd94h54c8rnztff9l82pp0zqnfvlwt77za8wjjsld36ms/smart/{query_data_encoded}"

    response = requests.get(url)
    if response.status_code != 200:
        st.error(f"Failed to fetch WESO balance for {address}. Error: {response.status_code} - {response.reason}")
        return 0
    data = response.json()
    return float(data.get("data", {}).get("balance", 0)) / 1_000_000

# Function to fetch native LUNC balance
def fetch_native_balance(address):
    url = f"https://terra-classic-lcd.publicnode.com/cosmos/bank/v1beta1/balances/{address}"
    response = requests.get(url)
    if response.status_code != 200:
        st.error(f"Failed to fetch balance for {address}. Error: {response.status_code} - {response.reason}")
        return 0

    data = response.json()
    balances = data.get("balances", [])
    for balance in balances:
        if balance.get("denom") == "uluna":
            return float(balance.get("amount", 0)) / 1_000_000
    return 0

# Function to fetch WESO curve info
def fetch_weso_curve_info():
    query_data = {
        "curve_info": {}
    }
    query_data_encoded = base64.b64encode(json.dumps(query_data).encode()).decode()
    url = f"https://terra-classic-lcd.publicnode.com/cosmwasm/wasm/v1/contract/terra13ryrrlcskwa05cd94h54c8rnztff9l82pp0zqnfvlwt77za8wjjsld36ms/smart/{query_data_encoded}"

    response = requests.get(url)
    if response.status_code != 200:
        st.error(f"Failed to fetch WESO curve info. Error: {response.status_code} - {response.reason}")
        return {}
    return response.json().get("data", {})

# Function to fetch Oracle prices
def fetch_oracle_prices():
    url = "https://oracle.lbunproject.tech:8443/latest"
    response = requests.get(url)
    if response.status_code != 200:
        st.error(f"Failed to fetch Oracle prices. Error: {response.status_code} - {response.reason}")
        return {}

    data = response.json()
    prices = {}
    for item in data.get("prices", []):
        denom = item.get("denom")
        price = item.get("price")
        if denom and price:
            prices[denom] = float(price)
    return prices

# Function to fetch additional query data
def fetch_data(contract_address, query_key, query_value=None):
    query_data = {query_key: query_value if query_value else {}}
    query_data_encoded = base64.b64encode(json.dumps(query_data).encode()).decode()
    url = f"https://terra-classic-lcd.publicnode.com/cosmwasm/wasm/v1/contract/{contract_address}/smart/{query_data_encoded}"

    response = requests.get(url)
    if response.status_code != 200:
        st.error(f"Failed to fetch {query_key}. Error: {response.status_code} - {response.reason}")
        return {}
    return response.json().get("data", {})

# Render data for multi-item queries
def render_list_query_results(title, data_list):
    st.markdown(f"### {title}")
    if not data_list:
        st.warning("No data available.")
    else:
        for item in data_list:
            st.json(item)

# Render single result queries
def render_query_result(title, result):
    st.markdown(f"### {title}")
    if not result:
        st.warning("No data available.")
    else:
        st.json(result)

# CSS styling for cards with light and dark mode support
st.markdown(
    """
    <style>
        .card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 16px;
            margin: 4px 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }

        /* Light mode styles */
        @media (prefers-color-scheme: light) {
            .card {
                background-color: #f9f9f9;
                color: #000;
            }
        }

        /* Dark mode styles */
        @media (prefers-color-scheme: dark) {
            .card {
                background-color: #2e2e2e;
                color: #ffffff;
                border: 1px solid #444;
            }
        }

        .card h4 {
            margin: 0 0 8px 0;
        }

        .card p {
            margin: 0;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Helper function to render a card
def render_card(col, title, value):
    with col:
        st.markdown(
            f"""
            <div class="card">
                <h4>{title}</h4>
                <p>{value}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

# Contract address for queries
CONTRACT_ADDRESS = "terra13ryrrlcskwa05cd94h54c8rnztff9l82pp0zqnfvlwt77za8wjjsld36ms"

# Tabs for navigation
tabs = st.tabs(["Metrics", "Advanced Queries"])

# Metrics Tab
with tabs[0]:
    try:
        # WESO Metrics Section
        st.markdown("### 📊 TBC Metrics")
        available_weso = fetch_weso_balance(CONTRACT_ADDRESS)
        weso_curve_info = fetch_weso_curve_info()
        tbc_reserve = fetch_native_balance(CONTRACT_ADDRESS)
        prices = fetch_oracle_prices()

        circulating_supply = float(weso_curve_info.get("supply", 0)) / 1_000_000
        spot_price = float(weso_curve_info.get("spot_price", 0)) / 1_000_000
        reserve = float(weso_curve_info.get("reserve", 0)) / 1_000_000
        tax_collected = float(weso_curve_info.get("tax_collected", 0)) / 1_000_000
        reserve_price = prices.get("LUNC", 0)

        total_supply = circulating_supply + available_weso
        price = spot_price * reserve_price
        market_cap = circulating_supply * price
        tvl = reserve * reserve_price

        metrics = [
            ("Available Supply", f"{available_weso:,.6f}"),
            ("Circulating Supply", f"{circulating_supply:,.6f}"),
            ("Total Supply", f"{total_supply:,.6f}"),
            ("Spot Price (LUNC Ratio)", f"{spot_price:.6f}"),
            ("Price (USD)", f"{price:,.6f}"),
            ("Market Cap (USD)", f"{market_cap:,.2f}"),
            #("Total Value Locked (USD)", f"{tvl:,.2f}"),
            ("Tax Collected (LUNC)", f"{tax_collected:,.6f}"),
            ("TBC Reserve (LUNC)", f"{tbc_reserve:,.6f}")
        ]

        for i in range(0, len(metrics), 2):
            cols = st.columns(2)
            render_card(cols[0], metrics[i][0], metrics[i][1])
            if i + 1 < len(metrics):
                render_card(cols[1], metrics[i+1][0], metrics[i+1][1])

        # Multisig Balances Section
        st.markdown("### 🔒 Multisig Balances")
        multisig_metrics = [
            ("Validators Pool (LUNC)", f"{fetch_native_balance('terra1fap9lefsjjvv0phhry8km2garv5cxnd9m5ne83uakg7cdqg5uvhqzjgtva'):,.6f}"),
            ("Reserve Pool (LUNC)", f"{fetch_native_balance('terra165qakktyzk5le5cwklj0elh7u2qsfq56kcgerggl6h5jd5uhmdpsswftv3'):,.6f}"),
            ("Operations Pool (LUNC)", f"{fetch_native_balance('terra10u93zelv44ddf3g82q7mrat43fey33etfwx5cnh5y2ryu73uvk4q0qytyd'):,.6f}"),
            ("Growth Pool (LUNC)", f"{fetch_native_balance('terra1xajrj06juslnjhnlwd4csay29yxaas2d5700seaccaa2gt9z54ms5wwyy7'):,.6f}"),
            ("Development Pool (LUNC)", f"{fetch_native_balance('terra1eah8zs7datkz67u56p0cu4kakf3dagy673axx7j0n4et5mvxk3ls6lm8z8'):,.6f}"),
            ("Mining Rewards (WESO)", f"{fetch_weso_balance('terra10c9w7pf02fr7v8xc66s6m0hf672rj07t28zhvquve6np7hgj368qes797c'):,.6f}")
        ]

        for i in range(0, len(multisig_metrics), 2):
            cols = st.columns(2)
            render_card(cols[0], multisig_metrics[i][0], multisig_metrics[i][1])
            if i + 1 < len(multisig_metrics):
                render_card(cols[1], multisig_metrics[i+1][0], multisig_metrics[i+1][1])

        # DAO Wallets Section
        st.markdown("### 🏛️ DAO Wallet Balances")
        dao_wallets = {

        }
        dao_metrics = [
            ("LUNC", f"{fetch_native_balance('terra1wkdm6wcm4srahrvp09jea7csfq3yuacc4gmyft6p6n6pls9wy5js9lqhqq'):,.6f}"),
            ("WESO ", f"{fetch_weso_balance('terra1wkdm6wcm4srahrvp09jea7csfq3yuacc4gmyft6p6n6pls9wy5js9lqhqq'):,.6f}")
        ]

        for i in range(0, len(dao_metrics), 2):
            cols = st.columns(2)
            render_card(cols[0], dao_metrics[i][0], dao_metrics[i][1])
            if i + 1 < len(dao_metrics):
                render_card(cols[1], dao_metrics[i+1][0], dao_metrics[i+1][1])
    
    
    except Exception as e:
        st.error(f"Error loading Metrics tab: {e}")

with tabs[1]:
    # New Advanced Queries Page
    st.markdown("### \U0001F4DD Advanced Contract Queries")
    try:
        # Fetch and display query results
        token_info = fetch_data(CONTRACT_ADDRESS, "token_info")
        render_query_result("Token Info", token_info)

        marketing_info = fetch_data(CONTRACT_ADDRESS, "marketing_info")
        render_query_result("Marketing Info", marketing_info)

        param_info = fetch_data(CONTRACT_ADDRESS, "param_info")
        # Adjust percentage values by dividing by 10 and formatting
        for key in ["reserve_pool_pct", "operations_pool_pct", "growth_pool_pct", "development_pool_pct", "project_tax_pct", "to_validator_pct", "phase_one_tax"]:
            if key in param_info:
                param_info[key] = f"{param_info[key] / 10:.1f}%"
        render_query_result("Param Info", param_info)

        acct_info = fetch_data(CONTRACT_ADDRESS, "acct_info")
        render_query_result("Account Info", acct_info)

        mining_info = fetch_data(CONTRACT_ADDRESS, "mining_info")
        render_query_result("Mining Info", mining_info)

        safety_info = fetch_data(CONTRACT_ADDRESS, "safety_info")
        render_query_result("Safety Info", safety_info)

    except Exception as e:
        st.error(f"Error loading queries: {e}")
