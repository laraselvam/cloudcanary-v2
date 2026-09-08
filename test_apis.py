import requests
import boto3

# Test 1: Azure Pricing API
print("=== Azure Pricing ===")
azure_url = "https://prices.azure.com/api/retail/prices?$filter=armRegionName eq 'centralindia' and serviceName eq 'Virtual Machines'"
response = requests.get(azure_url)
data = response.json()
print(f"Total items found: {len(data['Items'])}")
print(f"First item: {data['Items'][0]['productName']} - ${data['Items'][0]['retailPrice']}")

# Test 2: AWS Pricing API (using boto3)
print("\n=== AWS Pricing ===")
client = boto3.client('pricing', region_name='us-east-1')

aws_response = client.get_products(
    ServiceCode='AmazonEC2',
    Filters=[
        {'Type': 'TERM_MATCH', 'Field': 'instanceType', 'Value': 't3.micro'},
        {'Type': 'TERM_MATCH', 'Field': 'regionCode', 'Value': 'ap-southeast-2'},
        {'Type': 'TERM_MATCH', 'Field': 'operatingSystem', 'Value': 'Linux'},
        {'Type': 'TERM_MATCH', 'Field': 'tenancy', 'Value': 'Shared'},
        {'Type': 'TERM_MATCH', 'Field': 'preInstalledSw', 'Value': 'NA'},
        {'Type': 'TERM_MATCH', 'Field': 'capacitystatus', 'Value': 'Used'},
    ],
    MaxResults=1
)

import json
price_item = json.loads(aws_response['PriceList'][0])
terms = price_item['terms']['OnDemand']
first_term = list(terms.values())[0]
first_dimension = list(first_term['priceDimensions'].values())[0]
aws_price_per_hour = float(first_dimension['pricePerUnit']['USD'])
print(f"AWS t3.micro (ap-southeast-2): ${aws_price_per_hour}/hour")
# Test 3: electricityMap Carbon Intensity API
print("\n=== Carbon Intensity ===")
headers = {"auth-token": "em_nyjJayxDGctDEFweN4jbKXg89N49jQdR"}
carbon_url = "https://api.electricitymap.org/v3/carbon-intensity/latest?zone=IN"
carbon_response = requests.get(carbon_url, headers=headers)
carbon_data = carbon_response.json()
print(f"India carbon intensity: {carbon_data}")
au_carbon_url = "https://api.electricitymap.org/v3/carbon-intensity/latest?zone=AU-NSW"
au_carbon_response = requests.get(au_carbon_url, headers=headers)
au_carbon_data = au_carbon_response.json()
print(f"Australia carbon intensity: {au_carbon_data}")
import pandas as pd

# Combine data into a table
print("\n=== Combined Region Comparison ===")

comparison_data = {
    "Region": ["Azure Central India", "AWS ap-southeast-2"],
    "Provider": ["Azure", "AWS"],
    "Sample_Price_USD": [data['Items'][0]['retailPrice'], aws_price_per_hour],
    "Carbon_Intensity_gCO2": [carbon_data['carbonIntensity'], au_carbon_data['carbonIntensity']]
}

df = pd.DataFrame(comparison_data)
print(df)
# Scoring: lower is better. Normalize cost and carbon, then combine.
cost_weight = 0.5
carbon_weight = 0.5

max_cost = df['Sample_Price_USD'].astype(float).max()
max_carbon = df['Carbon_Intensity_gCO2'].astype(float).max()

df['Cost_Score'] = df['Sample_Price_USD'].astype(float) / max_cost
df['Carbon_Score'] = df['Carbon_Intensity_gCO2'].astype(float) / max_carbon
df['Total_Score'] = (cost_weight * df['Cost_Score']) + (carbon_weight * df['Carbon_Score'])

print("\n=== Scored Comparison ===")
print(df)

best_region = df.loc[df['Total_Score'].idxmin(), 'Region']
print(f"\n✅ Best region to run workload: {best_region}")
import subprocess

print(f"\n🚀 Provisioning workload in: {best_region}")

terraform_path = r"C:\Users\devan\Downloads\terraform_1.16.0_windows_amd64\terraform.exe"

# Apply
subprocess.run([terraform_path, "apply", "-auto-approve"])

print("\n✅ Workload deployed! Simulating job run...")
import time
time.sleep(5)

# Destroy
print("\n🧹 Cleaning up resources...")
subprocess.run([terraform_path, "destroy", "-auto-approve"])

print("\n✅ CloudCanary cycle complete!")