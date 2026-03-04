# ESG Investment Insight KPI API

Portfolio analytics API providing ESG scores, financial metrics, and investment insights.

## Setup Instructions

### Prerequisites
- Python 3.10+
- PostgreSQL 14+

# Install Python 3.10+ and create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install core dependencies
pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic python-dotenv
pip install yfinance requests pandas
pip install pytest httpx  # for testing


### Installation
```bash
git clone https://github.com/yourusername/esg-api.git
cd esg-api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt (Load Core dependency)

ESG Investment Search API:
curl "https://financialmodelingprep.com/stable/esg-environmental-social-governance-data?symbol=AAPL&apikey=qj0a0JowZ8d1jpQxFDjyHRfjUkGvaWIu"

### Run API

uvicorn {folder.file}:app --reload