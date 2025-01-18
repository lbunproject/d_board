import streamlit as st
import requests
import json
import base64

# Set page configuration
st.set_page_config(page_title="MESO Dashboard", layout="wide")

# Function to fetch MESO contract balance for a specific address
def fetch_meso_balance(address):
    query_data = {
        "balance": {"address": address}
    }
    query_data_encoded = base64.b64encode(json.dumps(query_data).encode()).decode()
    url = f"https://terra-classic-lcd.publicnode.com/cosmwasm/wasm/v1/contract/terra13ryrrlcskwa05cd94h54c8rnztff9l82pp0zqnfvlwt77za8wjjsld36ms/smart/{query_data_encoded}"

    response = requests.get(url)
    if response.status_code != 200:
        st.error(f"Failed to fetch MESO balance for {address}. Error: {response.status_code} - {response.reason}")
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

# Function to fetch MESO curve info
def fetch_meso_curve_info():
    query_data = {
        "curve_info": {}
    }
    query_data_encoded = base64.b64encode(json.dumps(query_data).encode()).decode()
    url = f"https://terra-classic-lcd.publicnode.com/cosmwasm/wasm/v1/contract/terra13ryrrlcskwa05cd94h54c8rnztff9l82pp0zqnfvlwt77za8wjjsld36ms/smart/{query_data_encoded}"

    response = requests.get(url)
    if response.status_code != 200:
        st.error(f"Failed to fetch MESO curve info. Error: {response.status_code} - {response.reason}")
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

# CSS styling for cards
st.markdown(
    """
    <style>
        .card {
            background-color: #f9f9f9;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 16px;
            margin: 4px 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
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
        st.markdown(f'<div class="card"><h4>{title}</h4><p>{value}</p></div>', unsafe_allow_html=True)

# Contract address for queries
CONTRACT_ADDRESS = "terra13ryrrlcskwa05cd94h54c8rnztff9l82pp0zqnfvlwt77za8wjjsld36ms"

# Tabs for navigation
tabs = st.tabs(["Metrics", "Advanced Queries"])

# Metrics Tab
with tabs[0]:
    try:
        # MESO Metrics Section
        st.markdown("### 📊 TBC Metrics")
        available_meso = fetch_meso_balance(CONTRACT_ADDRESS)
        meso_curve_info = fetch_meso_curve_info()
        prices = fetch_oracle_prices()

        circulating_supply = float(meso_curve_info.get("supply", 0)) / 1_000_000
        spot_price = float(meso_curve_info.get("spot_price", 0)) / 1_000_000
        reserve = float(meso_curve_info.get("reserve", 0)) / 1_000_000
        tax_collected = float(meso_curve_info.get("tax_collected", 0)) / 1_000_000
        reserve_price = prices.get("LUNC", 0)

        total_supply = circulating_supply + available_meso
        price = spot_price * reserve_price
        market_cap = circulating_supply * price
        tvl = reserve * reserve_price

        metrics = [
            ("Available Supply", f"{available_meso:,.6f}"),
            ("Circulating Supply", f"{circulating_supply:,.6f}"),
            ("Total Supply", f"{total_supply:,.6f}"),
            ("Spot Price (LUNC Ratio)", f"{spot_price:.6f}"),
            ("Price (USD)", f"{price:,.6f}"),
            ("Market Cap (USD)", f"{market_cap:,.2f}"),
            ("Total Value Locked (USD)", f"{tvl:,.2f}"),
            ("Tax Collected (LUNC)", f"{tax_collected:,.6f}")
        ]

        for i in range(0, len(metrics), 2):
            cols = st.columns(2)
            render_card(cols[0], metrics[i][0], metrics[i][1])
            if i + 1 < len(metrics):
                render_card(cols[1], metrics[i+1][0], metrics[i+1][1])

        # Multisig Balances Section
        st.markdown("### 🔒 Multisig Balances")
        multisig_metrics = [
            ("Mining Rewards (MESO)", f"{fetch_meso_balance('terra10c9w7pf02fr7v8xc66s6m0hf672rj07t28zhvquve6np7hgj368qes797c'):,.6f}"),
            ("Validators (LUNC)", f"{fetch_native_balance('terra1fap9lefsjjvv0phhry8km2garv5cxnd9m5ne83uakg7cdqg5uvhqzjgtva'):,.6f}")
        ]

        for i in range(0, len(multisig_metrics), 2):
            cols = st.columns(2)
            render_card(cols[0], multisig_metrics[i][0], multisig_metrics[i][1])
            if i + 1 < len(multisig_metrics):
                render_card(cols[1], multisig_metrics[i+1][0], multisig_metrics[i+1][1])

        # DAO Wallets Section
        st.markdown("### 🏛️ DAO Wallets Balances")
        dao_wallets = {
            "Al": "terra18jxqe39h43499zkcmqhmn37k25h7up3j4d8yee",
            "Di": "terra1j49q86q5xctmdmstzv4f344jwyhe94qyxfq90w",
            "Ri": "terra1mqr4x5hgdcqkcymzr7td2zpqq5epjcej00zd90",
            "Re": "terra1uvtvrqvxqwnj344zw4rz3l2h45y53qqemlxhz2",
        }
        dao_metrics = []
        for name, address in dao_wallets.items():
            balance = fetch_native_balance(address)
            dao_metrics.append((f"{name.capitalize()} (LUNC)", f"{balance:,.6f}"))

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
