# Stock Valuation & Risk Analytics API

> A comprehensive RESTful API for stock market analysis, valuation metrics, and risk assessment  
> **FastAPI • Python • PostgreSQL • Real-Time Updates**

[FastAPI](https://fastapi.tiangolo.com/)
[Python](https://www.python.org/)
[PostgreSQL](https://www.postgresql.org/)
[License](LICENSE)

---

## 📌 Submission Information

**Student:** Chun Ho Chui  
**Student ID:** 202030843  
**Module:** COMP3011 - Web Services and Web Data  
**Date:** March 10, 2026

### 📂 Deliverables


| Deliverable                    | Location                                                                                                   | Description                          |
| ------------------------------ | ---------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| **GitHub Repository**          | [https://github.com/errorstd/stock-valuation-api.git](https://github.com/errorstd/stock-valuation-api.git) | Full source code with commit history |
| **API Documentation (PDF)**    | `API-Documentation.pdf`                                                                                    | Complete endpoint reference          |
| **Technical Report (PDF)**     | `Technical-Report.pdf`                                                                                     | 5-page academic report               |
| **Presentation Slides (PPTX)** | `Presentation-Slides.pptx`                                                                                 | Oral exam presentation               |
| **Live API Docs (Swagger)**    | [http://localhost:8000/docs](http://localhost:8000/docs)                                                   | Interactive API documentation        |


---

## 🎯 Project Overview

This API provides financial analysis tools for stock market investors:

- **Stock Valuation** – Identify undervalued/overvalued stocks using P/E ratios
- **Risk Assessment** – Calculate volatility and risk classifications
- **Portfolio Analytics** – Track multi-stock portfolio performance
- **Sector Comparison** – Compare financial metrics across industries
- **Real-Time Updates** – Fetch latest data from Yahoo Finance API
- **Browse & Search** – Discover stocks by category, sector, or search term

### Project Evolution

Originally planned as an **ESG Investment API**, the project pivoted to financial valuation after encountering persistent API rate limiting issues with ESG data sources (100% failure rate on March 5, 2026). See **Technical Report** for detailed explanation of this strategic decision.

---

## 🛠️ Technology Stack


| Component           | Technology   | Version      | Purpose                                     |
| ------------------- | ------------ | ------------ | ------------------------------------------- |
| **Web Framework**   | FastAPI      | 0.109.0      | High-performance async API framework        |
| **Database**        | PostgreSQL   | 16           | Relational data storage with CASCADE DELETE |
| **ORM**             | SQLAlchemy   | 2.0.25       | Database abstraction layer                  |
| **Data Source**     | yfinance     | 0.2.36       | Yahoo Finance API wrapper                   |
| **Data Processing** | Pandas/NumPy | 2.2.0/1.26.3 | Financial calculations                      |
| **Server**          | Uvicorn      | 0.27.0       | ASGI production server                      |
| **Testing**         | pytest       | 8.0.0        | Automated testing framework (23 tests)      |


---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+ ([Download](https://www.python.org/downloads/))
- PostgreSQL 16+ ([Download](https://www.postgresql.org/download/))
- Git ([Download](https://git-scm.com/downloads))

### 1. Clone Repository

```bash
git clone https://github.com/errorstd/stock-valuation-api.git
cd risk-api
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup

Create `.env` file in project root:

```env
DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/stock_api
```

### 5. Initialize Database

```bash
python .\scripts\init_db.py
```

Expected output:

```
Creating all database tables...
✅ Database tables created successfully!
```

### 6. Import Stock Data

```bash
python -m scripts.data_import
```

This imports 150 companies across 8 sectors with 30 days of historical prices.

### 7. Start API Server

```bash
uvicorn app.main:app --reload
```

Output:

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### 8. Access Documentation

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 📚 API Documentation

### Core Endpoints (27 Total)

#### 🏢 Companies Management


| Method | Endpoint                   | Description                                |
| ------ | -------------------------- | ------------------------------------------ |
| GET    | `/companies/`              | List all companies or get specific company |
| POST   | `/companies/single`        | Create a single company from JSON          |
| POST   | `/companies/bulk`          | Bulk upload companies from CSV file        |
| DELETE | `/companies/{symbol}`      | Delete specific company (CASCADE)          |
| DELETE | `/companies/?confirm=true` | Delete all companies (CASCADE)             |


#### 🔄 Real-Time Updates **(NEW)**


| Method | Endpoint                     | Description                                |
| ------ | ---------------------------- | ------------------------------------------ |
| PUT    | `/companies/{symbol}/update` | Update single stock with real-time data    |
| PUT    | `/companies/update-all`      | Bulk update multiple stocks (up to 50)     |
| GET    | `/companies/{symbol}/live`   | Get live quote directly from Yahoo Finance |


#### 💰 Valuation Analytics


| Method | Endpoint                           | Description                       |
| ------ | ---------------------------------- | --------------------------------- |
| GET    | `/analytics/valuation/undervalued` | Find undervalued stocks (low P/E) |
| GET    | `/analytics/valuation/overvalued`  | Find overvalued stocks (high P/E) |


#### ⚠️ Risk Assessment


| Method | Endpoint                              | Description                |
| ------ | ------------------------------------- | -------------------------- |
| GET    | `/analytics/risk/volatility/{symbol}` | Calculate stock volatility |
| GET    | `/analytics/risk/high-risk`           | Identify high-risk stocks  |


#### 📊 Portfolio & Sectors


| Method | Endpoint                           | Description               |
| ------ | ---------------------------------- | ------------------------- |
| GET    | `/analytics/portfolio/performance` | Analyze portfolio metrics |
| GET    | `/analytics/sectors/comparison`    | Compare sectors           |
| GET    | `/sectors/`                        | List all sectors          |


#### 🔍 Browse & Search


| Method | Endpoint                 | Description                     |
| ------ | ------------------------ | ------------------------------- |
| GET    | `/browse/search?query=X` | Search stocks by name or symbol |
| GET    | `/browse/categories`     | Get all sectors and industries  |
| GET    | `/browse/new-stocks`     | Recently added stocks           |
| GET    | `/browse/tech-stocks`    | Technology sector stocks        |
| GET    | `/browse/green-energy`   | Green/renewable energy stocks   |


### Example API Calls

**Update Real-Time Data:**

```bash
curl -X PUT "http://localhost:8000/companies/AAPL/update"
```

**Find Undervalued Stocks:**

```bash
curl "http://localhost:8000/analytics/valuation/undervalued?limit=10&max_pe=15"
```

**Calculate Stock Volatility:**

```bash
curl "http://localhost:8000/analytics/risk/volatility/AAPL"
```

**Search Stocks:**

```bash
curl "http://localhost:8000/browse/search?query=apple"
```

**Portfolio Performance:**

```bash
curl "http://localhost:8000/analytics/portfolio/performance?symbols=AAPL,MSFT,GOOGL"
```

---

## 🗄️ Database Schema

```
companies (parent)
├── financial_metrics (CASCADE DELETE)
├── stock_prices (CASCADE DELETE)
└── esg_scores (CASCADE DELETE)
```

**Key Features:**

- **CASCADE DELETE** – Deleting company automatically removes all related data
- **Indexed columns** – `symbol`, `company_id`, `date` for fast queries
- **Foreign key constraints** – Ensures referential integrity

---

## 🧪 Testing

### Run All Tests

```bash
python run_all_tests.py
```

This executes:

- **Database tests** – Connection, CASCADE DELETE, foreign keys
- **API tests** – Endpoints, response formats
- **Analytics tests** – Calculation accuracy

### Run Individual Test Suites

```bash
# Database tests
python tests/test_db_connection.py

# API endpoint tests
python tests/test_api.py

# Analytics logic tests
python tests/test_analytics.py
```

**Test Results:**

- 23 automated tests
- 100% pass rate
- Performance: All endpoints < 500ms

### Manual Testing via Swagger UI

1. Open [http://localhost:8000/docs](http://localhost:8000/docs)
2. Click "Try it out" on any endpoint
3. Fill parameters and click "Execute"
4. View response

---

## 📁 Project Structure

```
stock-valuation-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI endpoints (27 routes)
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── database.py          # Database config
│   └── exceptions.py        # Custom error handlers
├── scripts/
│   ├── __init__.py
│   ├── data_import.py       # Data import (150 companies)
│   └── init_db.py           # Database setup script
├── tests/
│   ├── __init__.py
│   ├── run_all_tests.py     # Test runner
│   ├── test_db_connection.py  # Database tests
│   ├── test_api.py          # API endpoint tests
│   └── test_analytics.py    # Analytics logic tests
├── docs/
│   ├── API-Documentation.pdf   # Complete API reference
│   ├── Technical-Report.pdf    # Academic report (5 pages)
│   └── Presentation-Slides.pptx  # Oral exam slides
├── .env                     # Environment variables
├── .gitignore
├── requirements.txt         # Dependencies
├── README.md                # This file
```

---

## 🎓 Academic Context

### Key Learning Outcomes Demonstrated

- ✅ RESTful API design and implementation
- ✅ Database design with relational integrity
- ✅ External API integration (Yahoo Finance)
- ✅ Financial domain modeling
- ✅ Automated testing practices (23 tests)
- ✅ Technical documentation (Swagger + Report)
- ✅ Version control (Git with clear commit history)
- ✅ Strategic decision-making (ESG pivot)

### Generative AI Usage

This project utilized **Claude (Anthropic)** and **GitHub Copilot** as learning accelerators:

- **Level:** High-level use for creative thinking and solution exploration
- **Examples:** CASCADE DELETE understanding, volatility formula learning, strategic pivot decision
- **Verification:** All AI suggestions independently verified through testing and documentation research
- **Declaration:** Full GenAI usage declaration in Technical Report with conversation logs

See `Technical-Report.pdf` Section 5 for complete GenAI usage declaration.

---

## 📊 Data Coverage

- **150 companies** across 8 sectors
- **30 days** of historical stock prices per company
- **Sectors:** Technology, Finance, Healthcare, Energy, Consumer, Industrials, Real Estate, Utilities
- **Real-time updates** available via Yahoo Finance API

---

## 🚧 Known Limitations

1. **Data Source Dependency** – Relies on Yahoo Finance without paid backup
2. **No Authentication** – API publicly accessible without rate limiting
3. **Limited Financial Metrics** – Only basic valuation (P/E, EPS)
4. **Single Currency** – All values assumed USD
5. **No Real-Time Streaming** – Data requires manual refresh

See `Technical-Report.pdf` Section 7 for detailed limitations and future improvements.

---

## 📖 Documentation

- **Interactive API Docs (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Documentation (PDF):** `API-Documentation.pdf`
- **Technical Report (PDF):** `Technical-Report.pdf` (5 pages)
- **Presentation Slides:** `Presentation-Slides.pptx`

---

## 🤝 Contributing

This is an academic project for **COMP3011 coursework**. For questions or issues, please contact:

**Student:** Chun Ho Chui  
**Student ID:** 202030843  
**Email:** [wbvx0564@leeds.ac.uk](mailto:wbvx0564@leeds.ac.uk)

---

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **Yahoo Finance API** – Free financial data source
- **FastAPI Framework** – Automatic API documentation
- **PostgreSQL** – Robust relational database
- **COMP3011 Teaching Staff** – Course guidance and support

---

**Built with ❤️ for COMP3011 Web Services and Web Data**