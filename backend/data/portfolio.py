"""
Synthetic Indian Mutual Fund portfolio data.
Realistic fund names, expense ratios, categories based on real Indian MF market.
"""

SAMPLE_PORTFOLIO = {
    "age": 35,
    "risk_profile": "moderate",
    "monthly_income": 120000,
    "monthly_investment": 25000,
    "goals": ["retirement", "child_education"],
    "investment_horizon_years": 25,
    "portfolio": [
        {
            "fund_name": "Mirae Asset Large Cap Fund",
            "fund_id": "MALCF",
            "category": "Large Cap",
            "allocation_percent": 20,
            "invested_amount": 150000,
            "current_value": 187500,
            "sip_amount": 5000
        },
        {
            "fund_name": "Parag Parikh Flexi Cap Fund",
            "fund_id": "PPFCF",
            "category": "Flexi Cap",
            "allocation_percent": 20,
            "invested_amount": 150000,
            "current_value": 202500,
            "sip_amount": 5000
        },
        {
            "fund_name": "Axis Midcap Fund",
            "fund_id": "AMF",
            "category": "Mid Cap",
            "allocation_percent": 15,
            "invested_amount": 112500,
            "current_value": 128250,
            "sip_amount": 3750
        },
        {
            "fund_name": "Nippon India Small Cap Fund",
            "fund_id": "NISCF",
            "category": "Small Cap",
            "allocation_percent": 10,
            "invested_amount": 75000,
            "current_value": 97500,
            "sip_amount": 2500
        },
        {
            "fund_name": "HDFC Balanced Advantage Fund",
            "fund_id": "HBAF",
            "category": "Balanced Advantage",
            "allocation_percent": 10,
            "invested_amount": 75000,
            "current_value": 82500,
            "sip_amount": 2500
        },
        {
            "fund_name": "SBI Bluechip Fund",
            "fund_id": "SBIBC",
            "category": "Large Cap",
            "allocation_percent": 10,
            "invested_amount": 75000,
            "current_value": 88500,
            "sip_amount": 2500
        },
        {
            "fund_name": "ICICI Prudential Technology Fund",
            "fund_id": "ICICITECH",
            "category": "Sectoral - Technology",
            "allocation_percent": 8,
            "invested_amount": 60000,
            "current_value": 78000,
            "sip_amount": 2000
        },
        {
            "fund_name": "Kotak Gilt Fund",
            "fund_id": "KGF",
            "category": "Debt - Gilt",
            "allocation_percent": 7,
            "invested_amount": 52500,
            "current_value": 55125,
            "sip_amount": 1750
        }
    ]
}

FUND_METADATA_DB = {
    "MALCF": {
        "fund_name": "Mirae Asset Large Cap Fund",
        "category": "Large Cap",
        "benchmark": "Nifty 100 TRI",
        "expense_ratio": 0.54,
        "aum_cr": 37500,
        "fund_manager": "Gaurav Misra",
        "launch_year": 2008,
        "min_sip": 1000
    },
    "PPFCF": {
        "fund_name": "Parag Parikh Flexi Cap Fund",
        "category": "Flexi Cap",
        "benchmark": "Nifty 500 TRI",
        "expense_ratio": 0.63,
        "aum_cr": 62000,
        "fund_manager": "Rajeev Thakkar",
        "launch_year": 2013,
        "min_sip": 1000
    },
    "AMF": {
        "fund_name": "Axis Midcap Fund",
        "category": "Mid Cap",
        "benchmark": "Nifty Midcap 150 TRI",
        "expense_ratio": 0.52,
        "aum_cr": 24500,
        "fund_manager": "Shreyash Devalkar",
        "launch_year": 2011,
        "min_sip": 500
    },
    "NISCF": {
        "fund_name": "Nippon India Small Cap Fund",
        "category": "Small Cap",
        "benchmark": "Nifty Smallcap 250 TRI",
        "expense_ratio": 0.67,
        "aum_cr": 48000,
        "fund_manager": "Samir Rachh",
        "launch_year": 2010,
        "min_sip": 100
    },
    "HBAF": {
        "fund_name": "HDFC Balanced Advantage Fund",
        "category": "Balanced Advantage",
        "benchmark": "Nifty 50 TRI (60%) + Nifty Short Duration Debt Index (40%)",
        "expense_ratio": 0.74,
        "aum_cr": 85000,
        "fund_manager": "Gopal Agarwal",
        "launch_year": 1994,
        "min_sip": 100
    },
    "SBIBC": {
        "fund_name": "SBI Bluechip Fund",
        "category": "Large Cap",
        "benchmark": "S&P BSE 100 TRI",
        "expense_ratio": 0.85,
        "aum_cr": 42000,
        "fund_manager": "Sohini Andani",
        "launch_year": 2006,
        "min_sip": 500
    },
    "ICICITECH": {
        "fund_name": "ICICI Prudential Technology Fund",
        "category": "Sectoral - Technology",
        "benchmark": "BSE Teck TRI",
        "expense_ratio": 1.12,
        "aum_cr": 12000,
        "fund_manager": "Vaibhav Dusad",
        "launch_year": 2000,
        "min_sip": 100
    },
    "KGF": {
        "fund_name": "Kotak Gilt Fund",
        "category": "Debt - Gilt",
        "benchmark": "Nifty All Duration G-Sec Index",
        "expense_ratio": 0.45,
        "aum_cr": 3500,
        "fund_manager": "Abhishek Bisen",
        "launch_year": 1998,
        "min_sip": 500
    }
}

HISTORICAL_RETURNS_DB = {
    "MALCF": {
        "cagr_1y": 18.4,
        "cagr_3y": 14.2,
        "cagr_5y": 16.8,
        "cagr_10y": 15.1,
        "volatility_annual": 14.2,
        "max_drawdown": -28.5,
        "alpha": 1.8,
        "beta": 0.92
    },
    "PPFCF": {
        "cagr_1y": 22.1,
        "cagr_3y": 18.6,
        "cagr_5y": 19.4,
        "cagr_10y": 17.2,
        "volatility_annual": 13.8,
        "max_drawdown": -22.1,
        "alpha": 4.2,
        "beta": 0.85
    },
    "AMF": {
        "cagr_1y": 24.6,
        "cagr_3y": 19.8,
        "cagr_5y": 22.1,
        "cagr_10y": 18.9,
        "volatility_annual": 18.6,
        "max_drawdown": -32.4,
        "alpha": 3.1,
        "beta": 1.08
    },
    "NISCF": {
        "cagr_1y": 31.2,
        "cagr_3y": 24.8,
        "cagr_5y": 28.6,
        "cagr_10y": 22.4,
        "volatility_annual": 24.8,
        "max_drawdown": -42.1,
        "alpha": 6.8,
        "beta": 1.28
    },
    "HBAF": {
        "cagr_1y": 14.2,
        "cagr_3y": 12.8,
        "cagr_5y": 13.6,
        "cagr_10y": 12.1,
        "volatility_annual": 9.4,
        "max_drawdown": -18.2,
        "alpha": 1.2,
        "beta": 0.62
    },
    "SBIBC": {
        "cagr_1y": 16.8,
        "cagr_3y": 12.4,
        "cagr_5y": 14.2,
        "cagr_10y": 13.8,
        "volatility_annual": 15.1,
        "max_drawdown": -29.8,
        "alpha": 0.4,
        "beta": 0.95
    },
    "ICICITECH": {
        "cagr_1y": 28.4,
        "cagr_3y": 16.2,
        "cagr_5y": 24.8,
        "cagr_10y": 19.6,
        "volatility_annual": 26.4,
        "max_drawdown": -48.2,
        "alpha": 2.1,
        "beta": 1.42
    },
    "KGF": {
        "cagr_1y": 7.2,
        "cagr_3y": 6.8,
        "cagr_5y": 7.4,
        "cagr_10y": 7.8,
        "volatility_annual": 6.2,
        "max_drawdown": -8.4,
        "alpha": 0.2,
        "beta": 0.18
    }
}
