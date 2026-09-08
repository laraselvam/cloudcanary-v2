# 🌍 CloudCanary — Cost & Carbon Aware Multi-Cloud Scheduler

CloudCanary is a self-optimizing workload scheduler that automatically selects the best cloud region to deploy a workload, balancing **real-time cost** and **carbon emissions** across AWS and Azure.

## 🎯 Problem It Solves
Most cloud deployment decisions are made purely on cost, ignoring the environmental impact of where a workload runs. CloudCanary factors in both cost and carbon intensity to make sustainability-aware infrastructure decisions — automatically.

## ⚙️ How It Works
1. **Live Data Collection** — Fetches real-time EC2/VM pricing from AWS (via boto3) and Azure Retail Prices API, plus live grid carbon intensity from electricityMap for each region.
2. **Scoring Engine** — Normalizes cost and carbon values (0–1 scale) and combines them into a weighted Total Score per region.
3. **Automated Provisioning** — Uses Terraform to automatically provision an EC2 instance in the best-scoring region, run a simulated workload, and tear it down.
4. **Visualization** — A Streamlit dashboard displays live comparison tables, bar charts, and the selected best region.
5. **Historical Logging** — Every decision is logged to `decision_log.csv`, building a history of past scheduling decisions over time.

## 🌐 Regions Currently Supported
- Azure Central India
- AWS ap-southeast-2 (Sydney)
- AWS us-east-1 (N. Virginia)
- Azure UK South

## 🛠️ Tech Stack
- **Python** — core logic, data pipeline
- **AWS boto3** — EC2 pricing API
- **Azure Retail Prices API** — VM pricing
- **electricityMap API** — real-time carbon intensity
- **Terraform** — automated infrastructure provisioning/teardown
- **Streamlit** — interactive dashboard
- **Pandas** — data processing and scoring

## 🚀 Running Locally
```bash
pip install streamlit requests boto3 pandas
streamlit run dashboard.py