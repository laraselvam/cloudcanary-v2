import streamlit as st
import requests
import boto3
import json
import os
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="CloudCanary Dashboard", layout="wide")
st.title("🌍 CloudCanary — Cost & Carbon Aware Scheduler")

# ---- Region configs: add/remove entries here to change regions ----
REGIONS = [
    {
        "label": "Azure Central India",
        "provider": "Azure",
        "azure_region": "centralindia",
        "carbon_zone": "IN",
    },
    {
        "label": "AWS ap-southeast-2 (Sydney)",
        "provider": "AWS",
        "aws_region_code": "ap-southeast-2",
        "carbon_zone": "AU-NSW",
    },
    {
        "label": "AWS us-east-1 (N. Virginia)",
        "provider": "AWS",
        "aws_region_code": "us-east-1",
        "carbon_zone": "US-MIDA-PJM",
    },
    {
        "label": "Azure UK South",
        "provider": "Azure",
        "azure_region": "uksouth",
        "carbon_zone": "GB",
    },
]
import os
headers = {"auth-token": os.environ.get("ELECTRICITYMAP_API_KEY", "")}


def get_azure_price(azure_region):
    url = (
        f"https://prices.azure.com/api/retail/prices?$filter="
        f"armRegionName eq '{azure_region}' and serviceName eq 'Virtual Machines'"
    )
    resp = requests.get(url, timeout=30)
    data = resp.json()
    return data['Items'][0]['retailPrice']


def get_aws_price(region_code):
    client = boto3.client('pricing', region_name='us-east-1')
    aws_response = client.get_products(
        ServiceCode='AmazonEC2',
        Filters=[
            {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': 't3.micro'},
            {'Type': 'TERM_MATCH', 'Field': 'regionCode', 'Value': region_code},
            {'Type': 'TERM_MATCH', 'Field': 'operatingSystem', 'Value': 'Linux'},
            {'Type': 'TERM_MATCH', 'Field': 'tenancy', 'Value': 'Shared'},
            {'Type': 'TERM_MATCH', 'Field': 'preInstalledSw', 'Value': 'NA'},
            {'Type': 'TERM_MATCH', 'Field': 'capacitystatus', 'Value': 'Used'},
        ],
        MaxResults=1
    )
    price_item = json.loads(aws_response['PriceList'][0])
    terms = price_item['terms']['OnDemand']
    first_term = list(terms.values())[0]
    first_dimension = list(first_term['priceDimensions'].values())[0]
    return float(first_dimension['pricePerUnit']['USD'])


def get_carbon(zone_code):
    resp = requests.get(
        f"https://api.electricitymap.org/v3/carbon-intensity/latest?zone={zone_code}",
        headers=headers, timeout=30
    ).json()
    return resp['carbonIntensity']


rows = []
with st.spinner("Fetching live data for all regions..."):
    for region in REGIONS:
        try:
            if region["provider"] == "Azure":
                price = get_azure_price(region["azure_region"])
            else:
                price = get_aws_price(region["aws_region_code"])

            carbon = get_carbon(region["carbon_zone"])

            rows.append({
                "Region": region["label"],
                "Provider": region["provider"],
                "Price_USD": price,
                "Carbon_gCO2": carbon,
            })
        except Exception as e:
            st.warning(f"Could not fetch data for {region['label']}: {e}")

df = pd.DataFrame(rows)

if not df.empty:
    df['Cost_Score'] = df['Price_USD'] / df['Price_USD'].max()
    df['Carbon_Score'] = df['Carbon_gCO2'] / df['Carbon_gCO2'].max()
    df['Total_Score'] = 0.5 * df['Cost_Score'] + 0.5 * df['Carbon_Score']

    st.subheader("📊 Comparison Table")
    st.dataframe(df, use_container_width=True)

    st.bar_chart(df.set_index("Region")[["Cost_Score", "Carbon_Score"]])

    best_row = df.loc[df['Total_Score'].idxmin()]
    st.success(
        f"🏆 Best Region Selected: **{best_row['Region']}** "
        f"({best_row['Provider']}) — "
        f"Cost: ${best_row['Price_USD']:.4f}/hr | "
        f"Carbon: {best_row['Carbon_gCO2']:.0f} gCO2/kWh | "
        f"Score: {best_row['Total_Score']:.3f}"
    )

    # ---- Historical Logging ----
    log_file = "decision_log.csv"
    log_entry = pd.DataFrame([{
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Best_Region": best_row['Region'],
        "Provider": best_row['Provider'],
        "Price_USD": best_row['Price_USD'],
        "Carbon_gCO2": best_row['Carbon_gCO2'],
        "Total_Score": best_row['Total_Score'],
    }])

    if os.path.exists(log_file):
        log_entry.to_csv(log_file, mode='a', header=False, index=False)
    else:
        log_entry.to_csv(log_file, mode='w', header=True, index=False)

    st.subheader("📜 Decision History")
    st.dataframe(pd.read_csv(log_file), use_container_width=True)

else:
    st.error("No region data could be fetched. Check your network/API keys.")