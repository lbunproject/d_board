import streamlit as st
import requests
import json
import base64

# Set page configuration
st.set_page_config(page_title="WESO Dashboard", layout="wide")

# Function to fetch WESO contract balance for a specific address
def fetch_cw20_balance(cw20_address, address):
    query_data = {
        "balance": {"address": address}
    }

    query_data_encoded = base64.b64encode(json.dumps(query_data).encode()).decode()
    url = f"https://terra-classic-lcd.publicnode.com/cosmwasm/wasm/v1/contract/{cw20_address}/smart/{query_data_encoded}"

    response = requests.get(url)
    if response.status_code != 200:
        st.error(f"Failed to fetch CW20 balance for {address}. Error: {response.status_code} - {response.reason}")
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

# Function to fetch WESO curve info
def fetch_weso_token_info():
    query_data = {
        "token_info": {}
    }
    query_data_encoded = base64.b64encode(json.dumps(query_data).encode()).decode()
    url = f"https://terra-classic-lcd.publicnode.com/cosmwasm/wasm/v1/contract/terra13ryrrlcskwa05cd94h54c8rnztff9l82pp0zqnfvlwt77za8wjjsld36ms/smart/{query_data_encoded}"

    response = requests.get(url)
    if response.status_code != 200:
        st.error(f"Failed to fetch WESO token info. Error: {response.status_code} - {response.reason}")
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
        weso_curve_info = fetch_weso_curve_info()
        weso_token_info = fetch_weso_token_info()
        weso_tbc_reserve = fetch_native_balance(CONTRACT_ADDRESS)
        prices = fetch_oracle_prices()

        weso_circulating_supply = float(weso_curve_info.get("supply", 0)) / 1_000_000
        weso_spot_price = float(weso_curve_info.get("spot_price", 0)) / 1_000_000
        reserve = float(weso_curve_info.get("reserve", 0)) / 1_000_000
        tax_collected = float(weso_curve_info.get("tax_collected", 0)) / 1_000_000
        reserve_price = prices.get("LUNC", 0)

        total_supply = float(weso_token_info.get("total_supply", 0)) / 1_000_000
        price = weso_spot_price * reserve_price
        market_cap = weso_circulating_supply * price
        tvl = reserve * reserve_price
        available_weso = total_supply - weso_circulating_supply
        

        metrics = [
            ("Available Supply", f"{available_weso:,.6f}"),
            ("Circulating Supply", f"{weso_circulating_supply:,.6f}"),
            ("Total Supply", f"{total_supply:,.6f}"),
            ("Spot Price (LUNC Ratio)", f"{weso_spot_price:.6f} (${price:,.6f})"),
            ("Market Cap (USD)", f"${market_cap:,.2f}"),
            ("Total Value Locked (USD)", f"${tvl:,.2f}"),
            ("Tax Collected (LUNC)", f"{tax_collected:,.6f}"),
            ("TBC Reserve (LUNC)", f"{weso_tbc_reserve:,.6f} (${weso_tbc_reserve * reserve_price:,.2f})")
        ]

        for i in range(0, len(metrics), 2):
            cols = st.columns(2)
            render_card(cols[0], metrics[i][0], metrics[i][1])
            if i + 1 < len(metrics):
                render_card(cols[1], metrics[i+1][0], metrics[i+1][1])

        # DAO Wallets Section
        st.markdown("### 🏛️ Luna Classic DAO Treasury")
        tlnb = fetch_native_balance('terra1wkdm6wcm4srahrvp09jea7csfq3yuacc4gmyft6p6n6pls9wy5js9lqhqq')
        tlcw = fetch_cw20_balance('terra10fusc7487y4ju2v5uavkauf3jdpxx9h8sc7wsqdqg4rne8t4qyrq8385q6', 'terra1wkdm6wcm4srahrvp09jea7csfq3yuacc4gmyft6p6n6pls9wy5js9lqhqq')
        twcw = fetch_cw20_balance('terra13ryrrlcskwa05cd94h54c8rnztff9l82pp0zqnfvlwt77za8wjjsld36ms', 'terra1wkdm6wcm4srahrvp09jea7csfq3yuacc4gmyft6p6n6pls9wy5js9lqhqq')
        tbcw = fetch_cw20_balance('terra1uewxz67jhhhs2tj97pfm2egtk7zqxuhenm4y4m', 'terra1wkdm6wcm4srahrvp09jea7csfq3yuacc4gmyft6p6n6pls9wy5js9lqhqq')

        lunc_pool_amt = fetch_native_balance('terra1uewxz67jhhhs2tj97pfm2egtk7zqxuhenm4y4m')
        base_pool_amt = fetch_cw20_balance('terra1uewxz67jhhhs2tj97pfm2egtk7zqxuhenm4y4m','terra1uewxz67jhhhs2tj97pfm2egtk7zqxuhenm4y4m')
        base_spot_price = lunc_pool_amt / base_pool_amt

        dao_metrics = [
            ("LUNC", f"{tlnb:,.6f} (${tlnb * reserve_price:,.2f})"),
            ("cwLUNC ", f"{tlcw:,.6f} (${tlcw * reserve_price:,.2f})"),
            ("WESO ", f"{twcw:,.6f} (${twcw * weso_spot_price * reserve_price:,.2f})"),
            ("BASE ", f"{tbcw:,.6f} (${tbcw * base_spot_price * reserve_price:,.2f})"),
        ]

        for i in range(0, len(dao_metrics), 2):
            cols = st.columns(2)
            render_card(cols[0], dao_metrics[i][0], dao_metrics[i][1])
            if i + 1 < len(dao_metrics):
                render_card(cols[1], dao_metrics[i+1][0], dao_metrics[i+1][1])

        # Multisig Balances Section
        st.markdown("### 🔒 Sub-DAO Treasury Pools")
        vpnb = fetch_native_balance('terra17x9tpp4ngn7hywnaleeqwjszyzws7hpy8tx0w35swyevuf9g4c9ssl7tml')
        rpnb = fetch_native_balance('terra100gz7lhvehugvauqj9zwsyjy9vjzfxvr0cdd4vgq8k3nfc4w280qskc9cg')
        opnb = fetch_native_balance('terra1j485p4zca6dlsf0ltze6elv3haqqv7s9pz7rngywsvh5k45jvkvqpm0vnd')
        gpnb = fetch_native_balance('terra1hh3f6pd97n69xft4jx2540v5srp0lpq4dwl2cjzvjdkca4vrnvksw0lqy2')
        dpnb = fetch_native_balance('terra18nc742rm8ckmad0h56pqnquug6axlcmy988mavhruha209r8msfse2agex')
        mrcw = fetch_cw20_balance('terra13ryrrlcskwa05cd94h54c8rnztff9l82pp0zqnfvlwt77za8wjjsld36ms', 'terra1a7m26klph99gkyavt4aq6x3mcl363sy9ul7mc9983s0akq683sdq6lzzl7')

        multisig_metrics = [
            ("Validators Pool (LUNC)", f"{vpnb:,.6f} (${vpnb * reserve_price:,.2f})"),
            ("Reserve Pool (LUNC)", f"{rpnb:,.6f} (${rpnb * reserve_price:,.2f})"),
            ("Operations Pool (LUNC)", f"{opnb:,.6f} (${opnb * reserve_price:,.2f})"),
            ("Growth Pool (LUNC)", f"{gpnb:,.6f} (${gpnb * reserve_price:,.2f})"),
            ("Development Pool (LUNC)", f"{dpnb:,.6f} (${dpnb * reserve_price:,.2f})"),
            ("Mining Rewards (WESO)", f"{mrcw:,.6f} (${mrcw * price:,.2f})"),
        ]

        for i in range(0, len(multisig_metrics), 2):
            cols = st.columns(2)
            render_card(cols[0], multisig_metrics[i][0], multisig_metrics[i][1])
            if i + 1 < len(multisig_metrics):
                render_card(cols[1], multisig_metrics[i+1][0], multisig_metrics[i+1][1])   
    
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
