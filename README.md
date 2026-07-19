# 🚀 AIgnition – AI-Powered Marketing Forecasting Platform

AIgnition is an AI-powered marketing analytics platform that helps businesses transform raw marketing campaign data into predictive insights. By leveraging Machine Learning, the platform forecasts revenue, estimates Return on Ad Spend (ROAS), and analyzes campaign and channel performance, enabling marketers to make smarter, data-driven decisions.

---

# 📌 Problem Statement

Modern businesses advertise across multiple platforms such as **Google Ads, Meta Ads, Microsoft Ads, Shopify, and GA4**. While these platforms generate valuable data, marketers often struggle to:

- Consolidate campaign data from multiple sources.
- Predict future revenue and campaign performance.
- Estimate Return on Ad Spend (ROAS).
- Identify the best-performing campaigns and marketing channels.
- Optimize marketing budgets before launching campaigns.

Traditional dashboards focus on historical reporting rather than predicting future outcomes. This makes strategic decision-making difficult and often leads to inefficient budget allocation.

---

# 💡 Our Solution

AIgnition addresses these challenges by providing an end-to-end AI-powered forecasting platform.

The workflow is simple:

1. Upload a marketing campaign CSV.
2. Automatically detect and process the uploaded data.
3. Clean and preprocess the dataset.
4. Generate advanced marketing features through feature engineering.
5. Use a trained CatBoost Machine Learning model to forecast future revenue.
6. Predict future ROAS.
7. Analyze campaign-wise and channel-wise performance.
8. Present actionable insights through an interactive dashboard.

By combining intelligent preprocessing with machine learning, AIgnition enables marketers to move beyond descriptive analytics and make proactive, data-driven marketing decisions.

---

# ✨ Key Features

- 📤 Upload marketing campaign CSV files.
- 🤖 AI-powered revenue forecasting.
- 📈 ROAS prediction.
- 📊 Campaign-wise performance analysis.
- 🌐 Channel-wise performance comparison.
- 📉 Confidence-based forecasting (P10, P50, P90).
- ⚡ Fast REST API powered by FastAPI.
- 📚 Interactive API documentation using Swagger.

---

# 🧠 Machine Learning Pipeline

The forecasting engine is built using a **CatBoost Regressor** trained on marketing campaign datasets.

### Feature Engineering

The following features are generated before prediction:

- Budget Utilization
- Click Through Rate (CTR)
- Cost Per Click (CPC)
- Cost Per Mille (CPM)
- Conversion Rate
- Year
- Month
- Day
- Day of Week
- Week of Year
- Quarter
- Weekend Indicator

These engineered features significantly improve prediction quality and allow the model to better capture campaign performance patterns.

---

# 🛠️ Tech Stack

### Frontend
- React.js
- Vite
- Tailwind CSS
- Recharts

### Backend
- FastAPI
- Uvicorn
- Pydantic

### Machine Learning
- CatBoost
- Pandas
- NumPy
- Scikit-learn

### Development Tools
- Git
- GitHub
- Swagger UI

---

# 🎯 Expected Outcome

AIgnition empowers marketing teams to:

- Forecast future campaign revenue.
- Predict Return on Ad Spend (ROAS).
- Compare campaign and channel performance.
- Make informed budget allocation decisions.
- Reduce manual analysis through AI-driven forecasting.
- Improve marketing efficiency with predictive insights.

---

**Built for the NetElixir AI Hackathon 🚀**
