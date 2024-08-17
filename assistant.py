import json
import threading
import openai
import time
from email.header import decode_header
import requests
from datetime import datetime, timedelta, date
import pytz
import googlemaps
import os.path
import pickle
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import msal
from bs4 import BeautifulSoup
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
import re
import random
import sqlite3
import ast

# for openai api
model = "gpt-4o"
client = openai.OpenAI(api_key='INSERT OPENAI API KEY')

# assistant ids for openai assistants
initial_check = "asst_AgpNYTlu0cKXfzglbmhGao9v"
write_reply = "asst_7v1AMGQgh2MXlY9UBj4fxqiv"
determine_elements = "asst_N4VcdVw660EogvcPn2AVOGxq"
adjust_to_context = "asst_iSNdPPsYX5ynRLArEvolaghw"
adjust_to_advisor_style = "asst_wiL9QJQdvnz8DQAYyeqpNrT0"
RAGneed_docselect = "asst_joq1BHOuBYBpdsNJbY0phVGh"
verify_content_RAG = "asst_zWt7q7RiAAKWPLXwMZErOUC2"
final_context_check = "asst_mNAPnGeh4uYR5x6ODu5smCrj"
DOC_tax = "asst_O6xXoh1F1meTeo4PYeRddqGO"
DOC_mackenzie = "asst_58O9c080gTEUf7WcFBMoOehq"
rewrite_query = "asst_MdV744CENmg7UjThuwUxqXtH"
searchforfunds = "asst_MG8muaDmNiKsKHrLPdhMB5oS"
determine_if_portfolio_related = "asst_FnLZJ7AAKLAQVhGtXsKoFKLg"
intercept_if_portfolio_related = "asst_3PwTNC599vz1WwVhIWDyvVA5"
recognize_client = "asst_HYYe3E9xRT1jLzrAsocOuD0s"

# additional features assistants
provide_experts = "asst_BUeixSJUbbX09nlCHEWpcKFr"
provide_attachments = "asst_IMR78gX92B9tRELYpiHTVr7e"
provide_relevant_products = "asst_J71ZZjyri0d1umlUYIl1Frrj"
determine_meeting_time = "asst_OwhnSi3GOrPJT6PRfAJtA0rm"
recap_enquiry = "asst_k3BQa17DwSBmNrhP7y5Z9Y3O"

# command assistants
schedule_meeting_instead = "asst_KSiVOFfH0LVLrEBhcdazUPaY"
remove_detail = "asst_hZtJlmTBhZYLp8UIGMXquXxP"
add_detail = "asst_K4PejPeGIDGQsHTmxANYzIHZ"
more_casual = "asst_qsQqfRpCnbo3tIXNu8uFiG6T"
make_friendly = "asst_oPpOC11KRkFODLU3PGp3C0Jb"
make_professional = "asst_kseAJ6oCM57Ykr0VdOmMHUSz"
change_custom = "asst_rsX8uIFqgYqfhC4NAyzJjT3A"
translate = "asst_TanH9Ih7HroiSce400SQw6vy"
determine_salesopps = "asst_4UGhkjOyYdKNxEdw8OZ1yzV5"

# mutual fund library for reccomendations
funds = {
    "Mutual Funds": {
        "For technology sector exposure": {
            "Fund Name": "IG Mackenzie Global Science & Technology Fund",
            "Top 3 Holdings": [
            "NVIDIA Corp. (17.6%)",
            "Apple Inc. (17.2%)",
            "Microsoft Corp. (13.68%)"
            ],
            "Top 3 Regions": [
            "United States (85.7%)",
            "Japan (4.8%)",
            "Netherlands (3.2%)"
            ],
            "Top 3 Sectors": [
            "Semiconductors and semiconductor equipment (37.1%)",
            "Software (29.6%)",
            "Technology hardware, storage, and peripherals (18.0%)"
            ],
            "Risk Rating": "Medium to high",
            "Management Expense Ratio (MER)": "1.19% (Series F)",
            "Average Annual Compounded Return": "18.8%"
        },
        "For Emerging Markets Exposure": {
            "Fund Name": "Mackenzie Emerging Markets Fund",
            "Top 3 Holdings": [
                "Taiwan Semiconductor Manufacturing Co Ltd (8.0%)",
                "Tencent Holdings Ltd (4.7%)",
                "Samsung Electronics Co Ltd (3.0%)"
            ],
            "Top 3 Regions": [
                "China (26.7%)",
                "India (19.5%)",
                "Taiwan (18.8%)"
            ],
            "Top 3 Sectors": [
                "Information Technology (23.4%)",
                "Financials (19.4%)",
                "Consumer Discretionary (12.6%)"
            ],
            "Risk Rating": "Medium",
            "Management Expense Ratio (MER)": "1.06% (Series F)",
            "Average Annual Compounded Return": "7.9% (5 Years)"
        },
        "For global fixed-income": {
            "Fund Name": "Mackenzie Unconstrained Fixed Income Fund",
            "Top 3 Holdings": [
                "Mackenzie Canadian All Corporate Bond Index ETF (2.3%)",
                "Bundesobligation 2.10% 04-12-2029 (2.0%)",
                "United States Treasury 3.50% 02-15-2033 (1.9%)"
            ],
            "Top 3 Regions": [
                "United States (38.8%)",
                "Canada (36.0%)",
                "Mexico (4.5%)"
            ],
            "Top 3 Sectors": [
                "Corporate Bonds (59.7%)",
                "Foreign Fixed Income (14.7%)",
                "Cash & Equivalents (9.4%)"
            ],
            "Risk Rating": "Low",
            "Management Expense Ratio (MER)": "0.78% (Series F)",
            "Average Annual Compounded Return": "1.3% (5 Years)"
        },
        "For Canadian Equities": {
            "Fund Name": "IG FI Canadian Equity Fund",
            "Top 3 Holdings": [
                "Royal Bank of Canada (9.46%)",
                "Canadian Natural Resources Ltd (4.82%)",
                "Agnico Eagle Mines Ltd (Ontario) (4.32%)"
            ],
            "Top 3 Regions": [
                "Canada (91.71%)",
                "United States (6.30%)",
                "Bermuda (0.90%)"
            ],
            "Top 3 Sectors": [
                "Financials (26.72%)",
                "Energy (15.57%)",
                "Industrials (14.33%)"
            ],
            "Risk Rating": "Medium",
            "Management Expense Ratio (MER)": "0.92% (as of 03/31/2024)",
            "Average Annual Compounded Return": "11.05% (5 Years)"
        },
        "For International Equities": {
           "Fund Name": "Mackenzie International Dividend Fund",
            "Top 3 Holdings": [
                "Safran SA (5.4%)",
                "Taiwan Semiconductor Manufacturing Co Ltd (5.2%)",
                "Hannover Rueck SE (4.7%)"
            ],
            "Top 3 Regions": [
                "Japan (18.5%)",
                "France (15.6%)",
                "Netherlands (13.1%)"
            ],
            "Top 3 Sectors": [
                "Industrials (20.0%)",
                "Financials (17.5%)",
                "Information Technology (15.5%)"
            ],
            "Risk Rating": "Medium",
            "Management Expense Ratio (MER)": "1.06% (Series F)",
            "Average Annual Compounded Return": "0.6% (3 Years)"
        },
        "For a Canadian fund balanced between equities and fixed-income": {
            "Fund Name": "IG Mackenzie Mutual of Canada",
            "Top 3 Holdings": [
                "Royal Bank of Canada (3.39%)",
                "Toronto-Dominion Bank (1.84%)",
                "Ontario, Province of 4.15% 02-JUN-2034 (1.83%)"
            ],
            "Top 3 Regions": [
                "Canada (65.13%)",
                "United States (22.42%)",
                "United Kingdom (2.30%)"
            ],
            "Top 3 Sectors": [
                "Financials (17.70%)",
                "Information Technology (10.62%)",
                "Industrials (10.27%)"
            ],
            "Risk Rating": "Medium",
            "Management Expense Ratio (MER)": "0.92% (as of 03/31/2024)",
            "Average Annual Compounded Return": "8.55% (5 Years)"
        },
        "For Canadian Fixed-Income": {
            "Fund Name": "IG Mackenzie Canadian Corporate Bond Fund",
            "Top 3 Holdings": [
                "Algonquin Power & Utilities Corp 5.25% 18-JAN-2082 (2.05%)",
                "Canadian Imperial Bank of Commerce 2.75% 07-MAR-2025 (1.74%)",
                "Fairfax Financial Holdings Ltd 3.95% 03-MAR-2031 (1.53%)"
            ],
            "Top 3 Regions": [
                "Canada (90.62%)",
                "United States (4.58%)",
                "Jersey (1.09%)"
            ],
            "Top 3 Sectors": [
                "Corporate Notes/Bonds (79.23%)",
                "Fixed Income Other (17.20%)",
                "Cash Equivalents (1.30%)"
            ],
            "Risk Rating": "Low",
            "Management Expense Ratio (MER)": "0.34% (as of 03/31/2024)",
            "Average Annual Compounded Return": "2.52% (5 Years)"
        },
        "For US Equities": {
            "Fund Name": "iProfile U.S. Equity Private Pool",
            "Top 3 Holdings": [
                "Microsoft Corp (6.59%)",
                "NVIDIA Corp (5.98%)",
                "Apple Inc (5.47%)"
            ],
            "Top 3 Regions": [
                "United States (88.58%)",
                "Ireland (1.74%)",
                "Netherlands (1.16%)"
            ],
            "Top 3 Sectors": [
                "Information Technology (30.19%)",
                "Health Care (12.50%)",
                "Financials (9.74%)"
            ],
            "Risk Rating": "Medium",
            "Management Expense Ratio (MER)": "0.67% (as of 03/31/2024)",
            "Average Annual Compounded Return": "16.02% (5 Years)"
        },
        "For exposure to Europe": {
            "Fund Name": "Mackenzie Ivy European Fund",
            "Top 3 Holdings": [
                "Nestle SA (5.5%)",
                "Admiral Group PLC (5.5%)",
                "Auto Trader Group PLC (5.3%)"
            ],
            "Top 3 Regions": [
                "United Kingdom (37.4%)",
                "Switzerland (16.2%)",
                "Germany (14.1%)"
            ],
            "Top 3 Sectors": [
                "Industrials (20.3%)",
                "Consumer Staples (18.0%)",
                "Health Care (13.5%)"
            ],
            "Risk Rating": "Low to Medium",
            "Management Expense Ratio (MER)": "1.07% (Series F)",
            "Average Annual Compounded Return": "6.1% (5 Years)"
        },
        "For a Global fund that is balanced between equities and fixed-income": {
            "Fund Name": "Mackenzie Maximum Diversification Global Multi-Asset Fund",
            "Top 3 Holdings": [
                "Mackenzie Maximum Diversification All World Developed (41.2%)",
                "Mackenzie Maximum Diversification Emerging Markets Index ETF (10.0%)",
                "Mackenzie Anti-Benchmark Global Investment Grade (21.0%)"
            ],
            "Top 3 Regions": [
                "United States (43.6%)",
                "Canada (4.5%)",
                "Japan (4.4%)"
            ],
            "Top 3 Sectors": [
                "Fixed Income (39.6%)",
                "Health Care (11.9%)",
                "Financials (11.3%)"
            ],
            "Risk Rating": "Low to Medium",
            "Management Expense Ratio (MER)": "0.84% (Series F)",
            "Average Annual Compounded Return": "2.5% (Since Inception)"
        },
        "For a private investments option": {
            "Fund Name": "Mackenzie Northleaf Global Private Equity Fund",
            "Key Benefits": [
                "High absolute returns with lower volatility compared to public equities.",
                "Access to a diversified global private equity portfolio.",
                "Exposure to mid-market private companies for increased return opportunities."
            ],
            "Fund Structure": {
                "Private Equity Exposure": "75-80%",
                "Liquidity Sleeve – Public Investments": "20-25%"
            },
            "Key Terms": {
                "Minimum Initial Investment": "$25,000 accredited / $150,000 non-accredited",
                "Redemption Frequency": "Semi-annually (June/December)"
            },
            "Average Annual Private Equity Returns": {
                "Northleaf Private Equity Program": "22.4%",
            },
            "Management Expense Ratio (MER)": "A: 2.65%, F: 1.65%"
        },
        "For exposure to precious metals": {
            "Fund Name": "IG Mackenzie Global Precious Metals Fund",
            "Top 3 Holdings": [
                "Agnico Eagle Mines Ltd (Ontario) (10.05%)",
                "Barrick Gold Corp (4.73%)",
                "Alamos Gold Inc (4.35%)"
            ],
            "Top 3 Regions": [
                "Canada (62.63%)",
                "Australia (15.69%)",
                "South Africa (6.34%)"
            ],
            "Top 3 Sectors": [
                "Materials (88.32%)",
                "Foreign Equity (26.29%)",
                "Cash & Equivalents (2.36%)"
            ],
            "Risk Rating": "High",
            "Management Expense Ratio (MER)": "1.07% (as of 03/31/2024)",
            "Average Annual Compounded Return": "14.59% (5 Years)"
        }
    }
}

# fictional client portfolios
portfolios = {
     "Tim": {
        "mutual_funds": {
            "percentage of total portfolio": 55,
            "funds": [
                {
                    "name": "Mackenzie Ivy Growth and Income Fund",
                    "percentage of total portfolio": 15,
                    "description": "Seeks to provide long-term growth of capital by investing mainly in the equities of high-quality Canadian-based businesses and encompasses all fixed income products. Avoids passing fads in favour of disciplined acquisitions of undervalued businesses. Preservation of capital is the hallmark of the Fund’s investment approach",
                    "year_to_date_return_2024": 7.6
                },
                {
                    "name": "Mackenzie Strategic Bond Fund",
                    "percentage of total portfolio": 17,
                    "description": "Flexible mandate that can invest in a broad range of fixed income asset classes including non-investment-grade instruments. Exposure to high yield corporate bonds and floating rate loans can provide enhanced yield and protect against rising interest rates. Value added through longer-term positioning of term-to-maturity, credit selection and yield curve positioning",
                    "year_to_date_return_2024": -0.2
                },
                {
                    "name": "Mackenzie International Dividend Fund",
                    "percentage of total portfolio": 23,
                    "description": "Enhance portfolio construction with international businesses that have diverse revenue sources by geography, allowing for exposure to regions in different economic cycles. Focus on high-quality, dividend-paying companies with higher returns on invested capital.",
                    "year_to_date_return_2024": 7.5
                }
            ]
        },
        "etfs": {
            "percentage of total portfolio": 25,
            "funds": [
                {
                    "name": "Mackenzie Canadian Equity Index ETF",
                    "percentage of total portfolio": 14,
                    "description": "Market capitalization weighed indexing results in lower portfolio turnover and transaction costs versus other forms of indexing. Targeted access to specific market segments.",
                    "year_to_date_return_2024": 6.2
                },
                {
                    "name": "Mackenzie Maximum Diversification All World Developed Index ETF",
                    "percentage of total portfolio": 11,
                    "description": "Seeks to increase diversification to reduce biases and enhance risk-adjusted returns. Enhances diversification in global markets to reduce sector concentration, help protect value and give exposure to all sources of potential future return.",
                    "year_to_date_return_2024": 12.6
                }
            ]
        },
        "bonds": {
            "percentage of total portfolio": 20,
            "description": "A mix of long-term and short-term government bonds issued by the US, Canada, Sweden, and Denmark."
        },
        "total_portfolio_returns_year_to_date_2024": 12.2,
        "performance_expectations": "Given the year-to-date performance of the included components, the portfolio is expected to achieve a strong return for 2024."
    },
    "Olivia": {
        "etfs": {
            "percentage of total portfolio": 30,
            "funds": [
                {
                    "name": "Mackenzie Canada Low Volatility ETF",
                    "percentage of total portfolio": 18,
                    "description": "Serves as a core holding, offering capital appreciation potential while aiming to reduce overall portfolio volatility."
                },
                {
                    "name": "Mackenzie Maximum Diversification Emerging Markets Index ETF",
                    "percentage of total portfolio": 12,
                    "description": "Enhances diversification in Emerging Markets which are currently dominated by the Financial and Information Technology sectors."
                }
            ]
        },
        "individual_stocks": {
            "percentage of total portfolio": 50,
            "stocks": [
                {
                    "name": "Shopify",
                    "percentage of total portfolio": 6
                },
                {
                    "name": "Kinaxis",
                    "percentage of total portfolio": 7
                },
                {
                    "name": "Lightspeed Commerce",
                    "percentage of total portfolio": 3
                },
                {
                    "name": "Ballard Power Systems",
                    "percentage of total portfolio": 6
                },
                {
                    "name": "Docebo",
                    "percentage of total portfolio": 7
                },
                {
                    "name": "Absolute Software",
                    "percentage of total portfolio": 5
                },
                {
                    "name": "Descartes Systems Group",
                    "percentage of total portfolio": 7
                },
                {
                    "name": "Enghouse Systems",
                    "percentage of total portfolio": 4
                },
                {
                    "name": "Sierra Wireless",
                    "percentage of total portfolio": 3
                },
                {
                    "name": "BlackBerry",
                    "percentage of total portfolio": 2
                }
            ],
            "overall_return_year_to_date_2024": 22.0
        },
        "cryptocurrencies": {
            "percentage of total portfolio": 20,
            "assets": "Bitcoin, Ethereum, Solana",
            "year_to_date_return_2024": 35.0
        },
        "total_portfolio_returns_year_to_date_2024": 28.5,
        "performance_expectations": "Expected to achieve high returns given the focus on high-growth assets, though with significant volatility."
    },
    "Ethan": {
        "etfs": {
            "percentage of total portfolio": 16,
            "funds": [
                {
                    "name": "Mackenzie US Large Cap Equity Index ETF",
                    "percentage of total portfolio": 13,
                    "description": "Market capitalization weighed indexing results in lower portfolio turnover and transaction costs versus other forms of indexing."
                },
                {
                    "name": "Mackenzie Core Plus Global Fixed Income ETF",
                    "percentage of total portfolio": 3,
                    "description": "For investors seeking a long-term capital growth."
                }
            ]
        },
        "mutual_funds": {
            "percentage of total portfolio": 38,
            "funds": [
                {
                    "name": "Mackenzie Ivy Global Balanced Fund",
                    "percentage of total portfolio": 27,
                    "description": "A balanced fund that invests in both equities and fixed income, focusing on long-term growth and stability."
                },
                {
                    "name": "Mackenzie Canadian Growth Fund",
                    "percentage of total portfolio": 11,
                    "description": "Focuses on high-growth Canadian companies with strong potential for capital appreciation."
                }
            ]
        },
        "bonds": {
            "percentage of total portfolio": 21,
            "description": "A mix of Canadian government and corporate bonds for stability and income.",
            "year_to_date_return_2024": 3.0
        },
        "individual_stocks": {
            "percentage of total portfolio": 20,
            "sectors": [
                {
                    "name": "Technology Sector",
                    "percentage of total portfolio": 1.4,
                    "stocks": "only Apple",
                },
                {
                    "name": "Healthcare Sector",
                    "percentage of total portfolio": 10.6,
                    "stocks": "Johnson & Johnson, Pfizer, and UnitedHealth Group.",
                    "year_to_date_return_2024": 12.5
                },
                {
                    "name": "Consumer Goods Sector",
                    "percentage of total portfolio": 8,
                    "stocks": "Procter & Gamble, Coca-Cola, and Nestle.",
                    "year_to_date_return_2024": 0.5
                }
            ]
        },
        "total_portfolio_returns_year_to_date_2024": 16,
        "performance_expectations": "Expected to achieve moderate returns with a focus on stability and socially responsible investments."
    },
    "Natasha": {
        "etfs": {
            "percentage of total portfolio": 30,
            "funds": [
                {
                    "name": "Mackenzie Canadian Large Cap Equity Index ETF",
                    "percentage of total portfolio": 15,
                    "description": "Provides exposure to Canadian companies that consistently pay dividends."
                },
                {
                    "name": "Mackenzie Canadian Short-Term Bond Index ETF",
                    "percentage of total portfolio": 15,
                    "description": "Provides exposure to high-quality Canadian short-term bonds. Aims to provide stable income with low risk."
                }
            ]
        },
        "mutual_funds": {
            "percentage of total portfolio": 45,
            "funds": [
                {
                    "name": "Mackenzie Ivy Global Balanced Fund",
                    "percentage of total portfolio": 26,
                    "description": "A balanced fund that invests in both equities and fixed income, focusing on long-term growth and stability."
                },
                {
                    "name": "Mackenzie Bluewater Canadian Growth Fund",
                    "percentage of total portfolio": 19,
                    "description": "Focuses on high-growth Canadian companies with strong potential for capital appreciation."
                }
            ]
        },
        "bonds": {
            "percentage of total portfolio": 25,
            "description": "A mix of Canadian government and corporate bonds for stability and income.",
            "year_to_date_return_2024": 4.0
        },
        "total_portfolio_returns_year_to_date_2024": 11.4,
        "performance_expectations": "Expected to achieve moderate returns with a focus on stability and socially responsible investments."
    }
}

# fictional client profiles (incl. portfolio)
tim = {
    "context": {
        "Client name": "Tim Wilson",
        "Client age": 60,
        "Client location": "Montreal, QC",
        "Client occupation": "Lawyer",
        "Client financial literacy": "High",
        "Client family status": "Married, wife has high income so household does not rely on Tim's income",
        "Client financial goals": "Save sufficient funds to cover the cost of higher education for both children, purchase a vacation property in the next 5 years, build a robust retirement fund with the goal of retiring at around age 65.",
        "Client risk profile": "Moderate, willing to take some risks for potential higher returns but prefers a balanced approach. Comfortable with market fluctuations as long as there is a clear long-term strategy.",
        "Client investment preferences": "None",
        "Client income": "$250,000",
        "Client assets": "Primary residence valued at $1.5M. Condo in downtown Montreal valued at $900,000, often rented out for additional income.",
        "Client portfolio": portfolios["Tim"],
        "Client liabilities": "None.",
        "Past interactions with client": "None",
        "Advice given to client": "Recommended diversifying ETF holdings to include international markets to reduce risk and enhance potential returns. Suggested setting up a RESP (Registered Education Savings Plan) to take advantage of government grants and tax benefits for children’s education. Advised on optimizing the tax efficiency of the investment portfolio through strategic asset allocation and tax-advantaged accounts.",
        "Client previous questions and concerns": "How to maximize tax efficiency in his investments, including understanding tax-loss harvesting and the benefits of tax-advantaged accounts. Concerned about the impact of market volatility on his retirement goals and strategies to mitigate risks. Wants to ensure there are sufficient funds allocated for children's education without compromising other financial goals. Seeks advice on balancing mortgage repayments with ongoing investment contributions to optimize financial growth and debt management.",
        "Percentage of portfolio allocated to fixed-income": 0.42
    },
    "brief": {
        "Client age": 60,
        "Family status": "Married with 2 children",
        "Occupation": "Lawyer at mid-size law firm",
        "Financial literacy": "High",
        "Annual income": "$250,000",
        "AUM": "$1.3M",
        "Risk profile": "Moderate",
        "Mobile": "(407) 555-6738"
    }
}
olivia = {
    "context": {
        "Client name": "Olivia Bennet",
        "Client age": 29,
        "Client location": "Toronto, ON",
        "Client occupation": "Software Developer at a tech startup, specializing in AI and machine learning.",
        "Client financial literacy": "Medium",
        "Client family status": "Single, with no dependents. Enjoys traveling and participating in tech conferences.",
        "Client financial goals": "Build a diverse investment portfolio to achieve financial independence by age 45. Plans on buying a condo in the next few months.",
        "Client risk profile": "Very aggressive, willing to take significant risks for potentially higher returns. Comfortable with high market volatility.",
        "Client investment preferences": "Strong preference for high-growth tech stocks, cryptocurrencies, and innovative companies.",
        "Client income": "$150,000 annually, with stock options and bonuses based on company performance.",
        "Client assets": "Currently renting an apartment. Savings of $100,000. Investment portfolio worth $500,000, primarily in tech stocks and cryptocurrencies.",
        "Client portfolio": portfolios["Olivia"],
        "Client liabilities": "No significant debts.",
        "Past interactions with client": "Discussed the potential of diversifying into traditional asset classes to mitigate risk. Evaluated cryptocurrency investments and their long-term viability.",
        "Advice given to client": "Recommended diversifying into more stable investments like bonds and blue-chip stocks. Suggested setting up a TFSA (Tax-Free Savings Account) for tax-free growth. Advised on the importance of maintaining an emergency fund.",
        "Client previous questions and concerns": "Interested in the long-term potential of cryptocurrency investments. Seeks advice on selecting high-growth stocks.",
        "Percentage of portfolio allocated to fixed-income": 0
    },
    "brief": {
        "Client age": 29,
        "Family status": "Single, no dependents",
        "Occupation": "Software Developer at startup",
        "Financial literacy": "Medium",
        "Annual income": "$150,000",
        "AUM": "$500,000",
        "Risk profile": "Very aggressive",
        "Mobile": "(917) 555-1029"
    }
}
ethan = {
    "context": {
        "Client name": "Ethan Brown",
        "Client Age": 58,
        "Client location": "Toronto, ON",
        "Client occupation": "Senior Executive at a multinational corporation, specializing in corporate strategy and operations.",
        "Client financial literacy": "High financial literacy; has extensive experience with personal and business finance, understands complex financial concepts, and follows market trends closely.",
        "Client family status": "Married with two adult children, both of whom are financially independent. Enjoys traveling, golfing, and philanthropy.",
        "Client financial goals": "Preserve wealth while ensuring continued growth. Plan for a comfortable retirement with the ability to travel extensively. Establish a charitable foundation to support various causes.",
        "Client risk profile": "Conservative, focused on wealth preservation",
        "Client investment preferences": "None",
        "Client income": "$450,000 annually, with substantial bonuses and stock options.",
        "Client assets": "Primary residence valued at $3.5M. Vacation home in Muskoka valued at $2M. Investment portfolio worth $10M, diversified across various asset classes.",
        "Client portfolio": portfolios["Ethan"],
        "Client liabilities": "Mortgage: $1.6M remaining on primary residence, with a 3.5% fixed interest rate, up for renewal in 3 months.",
        "Past interactions with client": "Reviewed the performance of the investment portfolio and adjusted asset allocation to reduce risk and increase exposure to ESG investments. Discussed strategies for wealth preservation and estate planning.",
        "Advice given to client": "Recommended increasing allocation to fixed income for stability. Suggested setting up a family trust and charitable foundation. Advised on tax-efficient investment strategies and estate planning.",
        "Percentage of portfolio allocated to fixed-income": 0.54,
        "Client previous questions and concerns": "Interested in understanding the best ways to preserve wealth while still achieving growth. Concerns about market volatility and its impact on retirement plans. Seeks advice on philanthropic endeavors and establishing a charitable foundation."
        
    },
    "brief": {
        "Client age": 58,
        "Family status": "Married with two adult children, both financially independent",
        "Occupation": "Senior Executive at ABC Bank",
        "Financial literacy": "High",
        "Annual income": "$700,000",
        "AUM": "$10M",
        "Risk profile": "Moderate",
        "Mobile": "(312) 555-8674"
    }   
}
natasha = {
    "context": {
        "Client name": "Natasha Davis",
        "Client age": 47,
        "Client location": "Quebec City, QC",
        "Client occupation": "Small business owner, runs a successful chain of coffee shops.",
        "Client financial literacy": "Medium, has a good grasp of business finance but less experience with personal investments.",
        "Client family status": "Divorced with one teenage daughter named Ashley who plans to attend university in 2 years. Enjoys community events and charity work.",
        "Client financial goals": "Ensure daughter's university education is fully funded. Expand the business to new locations. Build a solid retirement fund and plan for semi-retirement at age 60.",
        "Client risk profile": "Moderate, seeks a balance between growth and stability. Willing to take some risks but prefers safer investments for long-term goals.",
        "Client investment preferences": "Interested in a balanced portfolio with a mix of equities and fixed-income securities.",
        "Client income": "$200,000 annually",
        "Client assets": "Primary residence valued at $1.2M. Business assets worth $700,000. Investment portfolio worth $350,000, condo valued at 700,000.",
        "Client portfolio": portfolios["Natasha"],
        "Client liabilities": "None",
        "Past interactions with client": "Discussed the importance of diversifying personal investments beyond the business. Evaluated options for funding daughter's education and expanding the business.",
        "Advice given to client": "Recommended setting up a RESP for daughter's education. Suggested increasing equity allocation for potential growth.",
        "Client previous questions and concerns": "Concerns about balancing business investments with personal financial goals. Seeks advice on the best ways to save for daughter's education. Interested in understanding socially responsible investing.",
        "Percentage of portfolio allocated to fixed-income": 0.3
    },
    "brief": {
        "Client age": 47,
        "Family status": "Divorced with one teenage daughter",
        "Occupation": "Small business owner, runs chain of coffee shops",
        "Financial literacy": "Medium",
        "Annual income": "$200,000",
        "AUM": "$600,000",
        "Risk profile": "Moderate",
        "Mobile": "(805) 555-4392"
    }
}

# credentials for ms graph api
CLIENT_ID = '0b204757-ba7f-4827-9f37-6da3bac5ee5b'
CLIENT_SECRET = '7c28Q~x~CEenx-QkPDG_Z~FLolraYvg1PvqEwajp'
TENANT_ID = '9585ffc6-31d1-4af4-9ab9-937b8242dd27'
AUTHORITY = f'https://login.microsoftonline.com/{TENANT_ID}'
SCOPE = ['https://graph.microsoft.com/Mail.ReadWrite']
TOKEN_CACHE_FILE = 'outlook_token_cache.json'

# functions related to microsoft authentication
def load_cache():
    cache = msal.SerializableTokenCache()
    if os.path.exists(TOKEN_CACHE_FILE):
        cache.deserialize(open(TOKEN_CACHE_FILE, "r").read())
    return cache
def save_cache(cache):
    if cache.has_state_changed:
        open(TOKEN_CACHE_FILE, "w").write(cache.serialize())
def get_access_token():
    cache = load_cache()
    app = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY, token_cache=cache)
    accounts = app.get_accounts()

    if accounts:
        result = app.acquire_token_silent(SCOPE, account=accounts[0])
        if "access_token" in result:
            save_cache(cache)
            return result['access_token']

    flow = app.initiate_device_flow(scopes=SCOPE)

    if "user_code" not in flow:
        raise Exception("Failed to create device flow")
    
    print(flow["message"])  # Instructions for user to authenticate

    result = app.acquire_token_by_device_flow(flow)
    
    if "access_token" in result:
        save_cache(cache)
        return result['access_token']
    else:
        raise Exception(f"Could not obtain access token: {result.get('error_description')}")


def read_recent_email():
    """
    This function reads the most recent unread email from the assistant@wealth-ai.xyz Outlook account using the Microsoft Graph API.
    
    Steps:
    1. Retrieves an access token to authenticate API requests.
    2. Fetches the most recent unread email using the Microsoft Graph API.
    3. If an unread email is found, extracts relevant details such as the email ID, sender's address, and subject.
    4. Fetches the body of the email, handling plain text for replies and parsing HTML for other emails.
    5. Cleans the email body by removing disclaimers and unwanted text.
    6. Marks the email as read after processing.
    7. Returns the sender's address, subject, and cleaned body of the email.
    
    Returns:
    - Tuple: (from_address, subject, body_text) if an email is found and processed successfully.
    - None: if no unread email is found or if an error occurs.
    """
    
    try:
        access_token = get_access_token()
        endpoint = 'https://graph.microsoft.com/v1.0/me/messages?$filter=isRead eq false&$top=1'
        headers = {
            'Authorization': 'Bearer ' + access_token,
            'Accept': 'application/json',
        }
        response = requests.get(endpoint, headers=headers)
        if response.status_code == 200:
            emails = response.json().get('value', [])
            if not emails:
                print("No new emails found")
                return None

            email = emails[0]
            email_id = email['id']
            from_address = email['from']['emailAddress']['address']
            subject = email['subject']

            # Fetch the body of the email
            endpoint = f'https://graph.microsoft.com/v1.0/me/messages/{email_id}'
            if subject.lower().startswith("re:"):
                headers['Prefer'] = 'outlook.body-content-type="text"'
            response = requests.get(endpoint, headers=headers)
            if response.status_code == 200:
                email_details = response.json()
                body_raw = email_details.get('body', {}).get('content', '')

                # if the incoming email is a reply the extracted text can simply be raw, otherwise it needs to be parsed and cleaned up:
                if subject.lower().startswith("re:"):
                    body_text = body_raw
                else:
                    soup = BeautifulSoup(body_raw, 'html.parser')
                    for br in soup.find_all("br"):
                        br.replace_with("\n")
                    for p in soup.find_all("p"):
                        p.insert(0, "\n")
                        p.append("\n")
                    body_text = soup.get_text()

                    disclaimer_text = (
                        r"This email communication and any files transmitted with it are CONFIDENTIAL and may contain LEGALLY PRIVILEGED information. If you are not the intended recipient, please notify us by telephone \(514-286-7400\) or by return email and delete this communication and any copy immediately. Thank you\.\n\n"
                        r"Ce courriel et ses fichiers attachés sont CONFIDENTIELS et peuvent contenir de l'information PRIVILEGIÉE. Si ce message vous est parvenu par erreur, veuillez nous en aviser par téléphone \(514-286-7400\) ou par retour de courriel et détruisez ce message et toute copie sans délai. Merci\."
                    )

                    body_text = re.sub(disclaimer_text, '', body_text, flags=re.DOTALL)

                    # Use regex to find "Subject:" and capture everything after it
                    match = re.search(r'Subject:.*?\n(.*)', body_text, re.DOTALL)
                    if match:
                        cleaned_body = match.group(1).strip()
                    else:
                        cleaned_body = body_text

                # Mark the email as read
                update_endpoint = f'https://graph.microsoft.com/v1.0/me/messages/{email_id}'
                data = {
                    "isRead": True
                }
                response = requests.patch(update_endpoint, headers=headers, json=data)
                
                print(f"From: {from_address}")
                print(f"Subject: {subject}")
                print(f"Body: {cleaned_body if not subject.lower().startswith('re:') else body_text}")

                return from_address, subject, cleaned_body if not subject.lower().startswith('re:') else body_text
            else:
                print(f"Failed to fetch email details: {response.status_code}, {response.text}")
        else:
            print(f"Error: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"An error occurred: {e}")

    return None

def send_email(to_email,subject,content):
    """
    This function sends an email using the SendGrid API.
    
    Arguments:
    - to_email: The recipient's email address (string).
    - subject: The subject of the email (string).
    - content: The HTML content of the email (string).
    
    Steps:
    1. Initialize the SendGrid API client using an API key.
    2. Define the sender's email address and prepare the recipient's email, subject, and content.
    3. Create a Mail object containing the sender, recipient, subject, and content.
    4. Convert the Mail object to a JSON representation.
    5. Send the email by making an HTTP POST request to SendGrid's /mail/send endpoint.
    6. Print the response status code to indicate success or failure.

    """
    api_key = 'ENTER SENDGRID API KEY'

    sg = sendgrid.SendGridAPIClient(api_key=api_key)
    from_email = Email("assistant@wealth-ai.xyz")
    to_email = To(to_email)
    subject = subject
    content = Content("text/html", content)
    mail = Mail(from_email, to_email, subject, content)

    # Get a JSON-ready representation of the Mail object
    mail_json = mail.get()

    # Send an HTTP POST request to /mail/send
    response = sg.client.mail.send.post(request_body=mail_json)
    print(response.status_code)

# execute_layer simply runs an instance of chatGPT with a given prompt and OpenAI assistant
# when the script is running, every time you see "💬 Response: ... " you're seeing a chatGPT response
def execute_layer(query, assistant_id, timeout=20):

    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": query,
            }
        ]
    )

    run = client.beta.threads.runs.create(thread_id=thread.id, assistant_id=assistant_id)

    start_time = time.time()
    while run.status != "completed":
        if time.time() - start_time > timeout:
            print("Run execution timed out.")
            return None
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
        time.sleep(1)
    else:
        print("Run Completed.")

    message_response = client.beta.threads.messages.list(thread_id=thread.id)
    messages = message_response.data

    if not messages or not messages[0].content or not messages[0].content[0].text:
        print("No response content found in messages.")
        return None

    latest_message = messages[0]
    print(f"💬 Response: {latest_message.content[0].text.value}")
    return latest_message.content[0].text.value

def get_calendar_info():
    """
    This function retrieves and processes the advisor's busy times from the Calendly API for the next 7 days.
    
    Steps:
    1. Calculate the current UTC time and the UTC time 7 days in the future.
    2. Format the start and end times in ISO 8601 format with UTC timezone.
    3. Send a GET request to the Calendly API to retrieve the advisor's busy times within the specified period.
    4. Convert the busy times from UTC to Toronto timezone and format them into natural language strings.
    5. Store each formatted busy time in a dynamically created variable and add it to a list.
    6. Print and return the list of busy times.

    Returns:
    - List of strings representing the user's busy periods in a natural language format.

    """
    start_time = datetime.utcnow()
    end_time = start_time + timedelta(days=7)

    # Format times in ISO 8601 format with UTC timezone
    start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    end_time_str = end_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

    url = "https://api.calendly.com/user_busy_times"

    querystring = {
        "user": "https://api.calendly.com/users/YOUR USER ID",
        "start_time": start_time_str,
        "end_time": end_time_str
    }

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer eyJraWQiOiIxY2UxZTEzNjE3ZGNmNzY2YjNjZWJjY2Y4ZGM1YmFmYThhNjVlNjg0MDIzZjdjMzJiZTgzNDliMjM4MDEzNWI0IiwidHlwIjoiUEFUIiwiYWxnIjoiRVMyNTYifQ.eyJpc3MiOiJodHRwczovL2F1dGguY2FsZW5kbHkuY29tIiwiaWF0IjoxNzIwOTc5NzAwLCJqdGkiOiI0NTYwNDE3ZC03ODVlLTQyMTMtYTMxMS04YTU5ZDBhYWQzMzEiLCJ1c2VyX3V1aWQiOiIzNDQ2Zjk5MS1kOGVjLTQ4NGEtODkxNi04YjU0ZDUyMDY5MzgifQ.W6-ttTcyvhRXbKPVvHxS7-4lk-VnERr4qWPigH-pqxFwuXXh3Cdllz3Vjx3hyL5ZHVzG6ZpMz6j1D24DXVNb4A"
    }

    response = requests.get(url, headers=headers, params=querystring)
    data = response.json()

    # Toronto timezone
    toronto_tz = pytz.timezone('America/Toronto')

    # List to store busy periods
    busy_times = []

    # Extract busy periods with start and end times in Toronto time zone, with natural language formatting
    for busy_period in data.get('collection', []):
        start_time_utc = datetime.strptime(busy_period.get('start_time'), "%Y-%m-%dT%H:%M:%S.%fZ")
        end_time_utc = datetime.strptime(busy_period.get('end_time'), "%Y-%m-%dT%H:%M:%S.%fZ")
        
        start_time_toronto = start_time_utc.replace(tzinfo=pytz.utc).astimezone(toronto_tz)
        end_time_toronto = end_time_utc.replace(tzinfo=pytz.utc).astimezone(toronto_tz)
        
        start_time_str = start_time_toronto.strftime("%A, %B %d, %Y from %I:%M %p")
        end_time_str = end_time_toronto.strftime("%I:%M %p")
        
        busy_times.append(f"Busy on {start_time_str} to {end_time_str}.")

    # List to store variables
    busy_time_vars = []

    # Assign each busy time to a variable and add to the list
    for i, busy_time in enumerate(busy_times):
        var_name = f'busy_time_{i+1}'
        vars()[var_name] = busy_time
        busy_time_vars.append(vars()[var_name])

    print(f"List generated: {busy_time_vars}")
    return busy_time_vars

def get_address(restaurant_name,api_key="ENTER YOUR GOOGLE CALENDAR API KEY"):
    """
    Uses the Google Places API to retrieve the address of a restaurant the advisor has added to their profile.
    """
    # Define the endpoint and parameters
    endpoint_url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {
        'input': restaurant_name,
        'inputtype': 'textquery',
        'fields': 'formatted_address',
        'key': api_key
    }

    # Make a request to the Google Places API
    response = requests.get(endpoint_url, params=params)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        if data.get('candidates'):
            address = data['candidates'][0].get('formatted_address')
            if address:
                return address
            else:
                return "Address not found."
        else:
            return "No results found."
    else:
        return f"Error: {response.status_code}"
def get_drive_time(origin, destination, api_key="ENTER YOUR GOOGLE CALENDAR API KEY"):
    """
    Uses the Google Places API to determine live driving time from advisor office location to a restaurant they have in their profile.
    """

    gmaps = googlemaps.Client(key=api_key)

    result = gmaps.distance_matrix(origins=[origin],
                                   destinations=[destination],
                                   mode="driving",
                                   departure_time=datetime.now())

    drive_time = result['rows'][0]['elements'][0]['duration']['text']
    drive_time_traffic = result['rows'][0]['elements'][0]['duration_in_traffic']['text']
    
    print(drive_time)
    print(drive_time_traffic)

    return drive_time, drive_time_traffic

def schedule_meeting(summary, location, description, start_datetime, end_datetime):
    """
    Schedules a meeting in Google Calendar.

    Args:
        summary (str): Summary of the event.
        location (str): Location of the event.
        description (str): Description of the event.
        start_datetime (str): Start datetime in 'YYYY-MM-DDTHH:MM:SS-07:00' format.
        end_datetime (str): End datetime in 'YYYY-MM-DDTHH:MM:SS-07:00' format.
    """
    
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    CREDENTIALS_FILE = '/Users/michaelgoralski/Desktop/Assistant Build/client_secret_77078900171-o0lp8vc8t2jgjf735qkk7evdpfh72obk.apps.googleusercontent.com.json'
    TOKEN_FILE = 'token.pickle'
    
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)
    
    service = build('calendar', 'v3', credentials=creds)
    
    # Create event
    event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {
            'dateTime': start_datetime,
            'timeZone': 'America/Toronto',
        },
        'end': {
            'dateTime': end_datetime,
            'timeZone': 'America/Toronto',
        },
        'attendees': [None],
    }

    event = service.events().insert(calendarId='primary', body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))

# with each email inquiry, the script stores the different pieces of generated content in a json file called shared_data in order for this content to be accesible throughout different functions.
# the below functions load that json file into a dict and then write that dict back to the json file after it has been altered, so that content is accesible in new instances of the script running.
def load_shared_data():
    shared_data_file = 'shared_data.json'
    try:
        with open(shared_data_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
def save_shared_data(data):
    shared_data_file = 'shared_data.json'
    with open(shared_data_file, 'w') as file:
        json.dump(data, file)

# below is the function that processes the client's email contents via numerous chatGPT instances to generate useful content for the advisor
# every time execute_layer is called, a chatGPT instance runs with the given prompt and bot/assistant
# the chatGPT instances are organized into threads that run simultaneously. most threads also include some non-LLM processing and put together html content based on chatGPT output
# refer to the flow chart of chatGPT instances in the README to better understand what this function is doing
def llm(user_input,from_address):
    event_2 = threading.Event()
    event_3 = threading.Event()
    event_4 = threading.Event()
    event_5 = threading.Event()
    event_6 = threading.Event()
    event_7 = threading.Event()
    event_8 = threading.Event()
    event_9 = threading.Event()
    event_10 = threading.Event()

    def task10():
        # this section assigns a value of 1-5 to the clients preferred risk profile, and another value 1-5 to the actual level of risk in their portfolio, and then compares the 2 figures to determine whether there is need for rebalancing.
        if shared_data['client profile']['context']["Percentage of portfolio allocated to fixed-income"] >= 0.7:
            portfolio_risk = 1
        elif shared_data['client profile']['context']["Percentage of portfolio allocated to fixed-income"] >= 0.5:
            portfolio_risk = 2
        elif shared_data['client profile']['context']["Percentage of portfolio allocated to fixed-income"] >= 0.3:
            portfolio_risk = 3    
        elif shared_data['client profile']['context']["Percentage of portfolio allocated to fixed-income"] > 0.1:
            portfolio_risk = 4
        else:
            portfolio_risk = 5

        risk_profile_mapping = {
            "Very conservative": 1,
            "Conservative": 2,
            "Moderate": 3,
            "Aggressive": 4,
            "Very aggressive": 5
        }
        risk_profile = shared_data['client profile']['brief']["Risk profile"]
        risk_profile_value = risk_profile_mapping.get(risk_profile)

        # if the client's risk profile is greater than the actual level of risk in their portfolio, html content for a rebalancing reccomendation is included as an 'opportunity'
        balance_rec = ""  
        if risk_profile_value > portfolio_risk:
            balance_rec = f"""
                        <div class="category">1. Portfolio Rebalancing</div>
                        <div class="rationale">Given client's desired risk profile is {risk_profile} and {str(shared_data['client profile']['context']['Percentage of portfolio allocated to fixed-income']*100)+'%'} of their portfolio is allocated to fixed-income, client should rebalance portfolio to include more equity holdings. <a style="color: grey;" href="https://www.mackenzieinvestments.com/en/investments/by-asset-class/equities?selectedGroup=mutual-fund">Learn more</a>.</div>
                        <br>
                        """

        compiled_recs = ""
        if balance_rec != "":
            compiled_recs += balance_rec
            x = 2
        else:
            x = 1

        prompt_sales = f"Client profile:\n\n{shared_data['client profile']['context']}"
        bot_output_profileopps = execute_layer(prompt_sales,determine_salesopps)
        bot_output_profileopps = json.loads(bot_output_profileopps)

        email_specific_opportunities = execute_layer(user_input,provide_relevant_products)

        # if there are any email specific opportunities that weren't already identified based on the client's portfolio, they are appended to the opportunities list
        if email_specific_opportunities is not None and email_specific_opportunities != "N/A":
            email_specific_opportunities = json.loads(email_specific_opportunities)
            for key, value in email_specific_opportunities.items():
                if key not in bot_output_profileopps:
                    bot_output_profileopps[key] = value

        reference = {
            "private asset funds": {
                "name": "Private Asset Funds",
                "link": "https://www.mackenzieinvestments.com/en/investments/by-asset-class/private-markets"
            },
            "term life insurance": {
                "name": "Term Life Insurance",
                "link": "https://www.canadalife.com/insurance/life-insurance/term-life-insurance.html?cpcsource=google&cpcmedium=cpc&cpccampaign=CL_BRAND_PROTECT_TERM_S_EN&adgroup=BRANDED&gad_source=1&gclid=Cj0KCQjwv7O0BhDwARIsAC0sjWOh33BwFUd8Y0ScH9xLgvRc_y3zHqhbjLjH4i837IgekM7NyZYpYDUaAt4qEALw_wcB"
            },
            "whole life insurance": {
                "name": "Whole Life Insurance",
                "link": "https://www.canadalife.com/insurance/life-insurance/permanent-life-insurance.html"
            },
            "par-whole life insurance": {
                "name": "Par-whole Life Insurance",
                "link": "https://www.canadalife.com/insurance/life-insurance/permanent-life-insurance/participating-whole-life-insurance.html?cpcsource=google&cpcmedium=cpc&cpccampaign=FALL_BRAND_PROTECT_2022_CA_B-M_S_EN_PBM&gad_source=1&gclid=Cj0KCQjwv7O0BhDwARIsAC0sjWNsNvE3-hHTSgOiWTpqA66wvZXl5QOYi9k0ia5GgSxpcL1Psv-74mIaAhxaEALw_wcB"
            },
            "disability and critical illness insurance": {
                "name": "Disability & Critical Illness Insurance",
                "link": "https://www.canadalife.com/blog/insurance/disability-vs-critical-illness-insurance-whats-the-difference.html"
            },
            "creditor insurance": {
                "name": "Creditor Insurance",
                "link": "https://www.nesto.ca/mortgage-basics/what-is-mortgage-loan-insurance-aka-mortgage-default-insurance/"
            },
            "mortgage": {
                "name": "Mortgage",
                "link": "https://www.nesto.ca/"
            },
            "hisa": {
                "name": "HISA",
                "link": "https://www.ig.ca/en"
            },
            "secured lending": {
                "name": "Secured Lending",
                "link": "https://www.ig.ca/en/how-we-help/cash-management/personal-loan"
            },
            "estate settlement": {
                "name": "Estate Settlement",
                "link": "https://www.clearestate.com/"
            }
        }

        #for every product in the identified opportunities list, the appropriate html content to added to compiled_recs, which will be part of the final htlm response to the advisor
        for i, (product_key, rationale) in enumerate(bot_output_profileopps.items(), start=x):
            if product_key in reference:
                product_info = reference[product_key]
                compiled_recs += f"""
                <div class="category">{i}. {product_info['name']}</div>
                <div class="rationale">{rationale} <a style="color: grey;" href="{product_info['link']}">Learn more</a>.</div>
                <br>
                """
        
        shared_data['sales opportunities'] = compiled_recs
        event_10.set()
        print("Task 10 finished")

    def task9():
        prompt_searchfunds = f"Email:{user_input}\n\nFund Database:{funds}"
        shared_data['suggested funds'] = execute_layer(prompt_searchfunds,searchforfunds)
        event_9.set()
        print("Task 9 finished")

    def task2():
        shared_data['suggested experts'] = execute_layer(user_input,provide_experts)

        shared_data['enquiry recap'] = execute_layer(user_input,recap_enquiry)
        event_2.set()
        print("Task 2 finished")

    def task3():
        event_9.wait()
        
        output = execute_layer(f"Email:\n\n{user_input}\n\nPortfolio Info:\n\n{shared_data['client profile']['context']['Client portfolio']}\n\nFund suggestions:\n{shared_data['suggested funds']}",intercept_if_portfolio_related)
        if output.strip().lower() == "not portfolio related.":
           shared_data['last reply'] = execute_layer(user_input,write_reply)
           shared_data['thread 3, portfolio-related verdict'] == 'no'
        else:
           shared_data['last reply'] = output
           shared_data['thread 3, portfolio-related verdict'] == 'yes'

        event_3.set()
        print("Task 3 finished")

    def task4():
        shared_data['relevant elements'] = execute_layer(user_input,determine_elements)
        print(f"elements:{shared_data['relevant elements']}")
        event_4.set()
        print("Task 4 finished")

    def task5():
        shared_data['is portfolio related'] = execute_layer(user_input,determine_if_portfolio_related)
        if shared_data['is portfolio related'] != "Portfolio related":
            shared_data[from_address]['concise question'] = execute_layer(user_input,rewrite_query)
            shared_data['rag verdict'] = execute_layer(shared_data[from_address]['concise question'],RAGneed_docselect)
        else:
            shared_data['rag verdict'] = "No RAG needed."
        event_5.set()
        print("Task 5 finished")

    def task6():
        shared_data['relevant attachments'] = execute_layer(user_input,provide_attachments)
        event_6.set()
        print("Task 6 finished")

    def task7():
        event_3.wait()
        event_4.wait()
        
        if shared_data['relevant elements'] != "None":
            keys_of_interest = [key.strip() for key in shared_data['relevant elements'].split(",")]
           
            # if the inquiry is portfolio related, then the client's portfolio has already been taken into account and should therefore be removed from relevant elements of context at this stage
            if shared_data['thread 3, portfolio-related verdict'] == 'yes':
                if 'Client portfolio' in keys_of_interest:
                    keys_of_interest.remove('Client portfolio')

            print(f"keys:{keys_of_interest}")
    
            # once the relevant elements of context have been identified, content is pulled from the client profile for every key
            shared_data['selected context'] = '\n\n'.join([f"{key}: {shared_data['client profile']['context'][key]}" for key in keys_of_interest if key in shared_data['client profile']['context']])
            print(f"selected context:{shared_data['selected context']}")
            
            if keys_of_interest:
                prompt_contextcheck = f"Email:\n{shared_data['last reply']}\n\nAdditional context:\n{shared_data['selected context']}\n\nFund suggestions:\n{shared_data['suggested funds']}"
                print(f"CONTEXT CHECK PROMPT:\n\n{prompt_contextcheck}")
                shared_data['last reply'] = execute_layer(prompt_contextcheck,adjust_to_context)

        event_7.set()
        print("Task 7 finished")

    def task8():
        event_7.wait()
        event_5.wait()
        # below is the RAG component
        
        #initializes a place to store all the retrieved content
        shared_data[from_address]['all retrieved content'] = ""

        if shared_data['rag verdict'] != "No RAG needed.":
            # this iterates through all the RAG documents deemed relevant to the inquiry, retrieving relevant info and using it to verify accuracy of email each time
            # to include another RAG document, add document name and corresponding assistant id to below list
            docs = [
                {"Name": "Canadian Income Tax Act", "Bot":DOC_tax},
            ]
            for doc in docs:
                if doc["Name"] in shared_data['rag verdict']:
                    retrieved_content = execute_layer(shared_data[from_address]['concise question'],doc["Bot"])
                    prompt_RAGadj = f"Email:\n\n'{shared_data['last reply']}'\n\nVerified Information:\n\n'{retrieved_content}'"
                    shared_data['last reply'] = execute_layer(prompt_RAGadj,verify_content_RAG)
                    shared_data[from_address]['all retrieved content'] = shared_data[from_address]['all retrieved content'] + "\n\n" + retrieved_content
        
        with open('advisor_profile.json', 'r') as f:
            advisor_profile = json.load(f)

        prompt_adjusttoadvisor = f"Email:\n\n{shared_data['last reply']}\n\nAdvisor Info:{advisor_profile}"
        shared_data['styled reply'] = execute_layer(prompt_adjusttoadvisor,adjust_to_advisor_style)

        busy_times = get_calendar_info()         

        # a condensed version of the advisor profile to be used in prompts where the entire profile is not necessary
        shared_data['Core advisor profile'] = {
            "tone": advisor_profile["tone"],
            "phrasing": advisor_profile["phrasing"],
            "sign_off": advisor_profile["sign_off"],
            "other_clauses_preferences": advisor_profile["other_clauses_preferences"]
        }

        locations_raw = advisor_profile['locations']

        locations = {item.split(": ")[0]: item.split(": ")[1] for item in locations_raw}

        # fetches the addresses for the restaurants in the advisor's profile
        dinner_address = get_address(locations['Dinner'])
        lunch_address = get_address(locations['Lunch'])


        # fetches the driving time from the advisor's office to the restaurants in the advisor's profile
        d_drive_time, shared_data['d_drive_time_traffic'] = get_drive_time(locations['Office'],dinner_address)
        l_drive_time, shared_data['l_drive_time_traffic'] = get_drive_time(locations['Office'],lunch_address)

        today = date.today().strftime("%A, %B %d")

        info_meetings = {
            "Today's date": today,
            "Advisor busy times": busy_times,
            "Lunch meetings": {'restaurant you should propose': locations["Lunch"], 'driving time':shared_data['l_drive_time_traffic']},
            "Dinner meetings": {'restaurant you should propose': locations["Dinner"], 'driving time':shared_data['d_drive_time_traffic']}
        }

        prompt_final_check = f"Email:\n\n{user_input}\n\nReply:\n\n{shared_data['styled reply']}\n\nInfo to use for meetings: {info_meetings}\n\nEmail preferences:{shared_data['Core advisor profile']}"
        print(f"FINAL CHECK PROMPT:{prompt_final_check}")
        shared_data[from_address]['email 1'] = execute_layer(prompt_final_check,final_context_check)

        #generates email 2, a more detailed version of email 1
        prompt_moredetail = f"Email:\n\n{shared_data[from_address]['email 1']}\n\nAdditional info (if any):\n\n{shared_data[from_address]['all retrieved content']}\n\n{shared_data['selected context']}\n\nEmail preferences:{shared_data['Core advisor profile']}"
        shared_data[from_address]['email 2'] = execute_layer(prompt_moredetail,add_detail)

        # creates a 'snapshot' of the client profile to be included in the output to the advisor
        shared_data['basic client info'] = "<br>".join([f"{key}: {value}" for key, value in shared_data['client profile']['brief'].items()])
        event_8.set()
        print("Task 8 finished")

    def task11():
        event_2.wait()
        event_3.wait()
        event_4.wait()
        event_5.wait()
        event_6.wait()
        event_7.wait()
        event_8.wait()
        event_9.wait()
        event_10.wait()
        # this task waits for all the previous tasks to complete and then formats all the html and compiles it into one final html string that will be the body of the email being send to the advisor
        
        shared_data[from_address]['email 1'] = shared_data[from_address]['email 1'].replace('\n', '<br>')
        shared_data[from_address]['email 2'] = shared_data[from_address]['email 2'].replace('\n', '<br>')
        if shared_data['relevant attachments'] != None:
            shared_data['relevant attachments'] = shared_data['relevant attachments'].replace('\n', '<br>')
        if shared_data['suggested experts'] != None:
            shared_data['suggested experts'] = shared_data['suggested experts'].replace('\n', '<br>')
    
        # randomly chooses one of the 2 promo banner options 
        version_a = '<p><strong>Promo!</strong> Fixed rate 4 year mortgage: 5.29%. <a href="http://nesto.ca" style="color: #ffffff; text-decoration: underline;">Learn more</a>.</p>'    
        version_b = '<p><strong>Promo!</strong> Earn up to 5.00% with a HISA. <a href="https://www.ig.ca/en/how-we-help/cash-management/preferred-savings-account" style="color: #ffffff; text-decoration: underline;">Learn more</a>.</p>'
        shared_data['promo version'] = random.choice([version_a,version_b])

        # html string for the body of the email to be sent back to the advisor
        shared_data['final output'] = f"""
        <html>
        <head>
            <style>
            body {{
                font-family: Arial, sans-serif;
                color: #333333;
                background-color: #ffffff;
                padding: 0px;
                font-size: 0.9em; /* Slightly smaller text */
            }}
            .email-container {{
                background-color: #ffffff;
                padding: 5px;
            }}
            .rationale {{
                margin-top: 10px;
                margin-bottom: 5px;
                color: #000000; /* Changed rationale text to black */
                font-size: 0.9em; /* Slightly smaller text */
            }}
            .promo-banner {{
                text-align: center;
                padding: 1px 10px;
                border-radius: 2px;
                background-color: #a10606;
                color: #ffffff;
                font-size: 0.9em; /* Slightly smaller text */
            }}
            h3 {{
                color: #2a52be; /* Darker blue color */
                font-family: 'Open Sans', sans-serif; /* Open Sans Bold font */
                font-weight: 700;
                font-size: 1.1em; /* Slightly smaller text */
            }}
            p {{
                line-height: 1.5;
                font-size: 0.9em; /* Slightly smaller text */
            }}
            .divider {{
                border-top: 1px solid #cccccc;
                margin: 20px 0;
            }}
            .footer-logo {{
                display: flex;
                justify-content: center;
                align-items: center;
                height: 25px;
                padding: 15px 0;
                background-color: #FFFFFF;
            }}
            .footer-logo img {{
                width: 120px;
                height: auto;
            }}
            @media (prefers-color-scheme: dark) {{
                .footer-logo-light {{
                    display: none !important;
                }}
                .footer-logo-dark {{
                    display: block !important;
                }}
            }}
            @media (prefers-color-scheme: light) {{
                .footer-logo-light {{
                    display: block !important;
                }}
                .footer-logo-dark {{
                    display: none !important;
                }}
            }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <p style="color: grey; font-size: 0.9em; padding-top: 10px; padding-bottom: 5px;"><i><b>Summary of inquiry: </b>{shared_data['enquiry recap']}</i></p>
                <div class="divider"></div>
                <h3>REPLY OPTION 1</h3>
                <p>{shared_data[from_address]['email 1']}<br></p>
                <h3>REPLY OPTION 2</h3>
                <p>{shared_data[from_address]['email 2']}<br></p>
                <div class="divider"></div>
                <h3>OPPORTUNITIES</h3>
                {shared_data['sales opportunities']}
                <div class="divider"></div>
                <div class="promo-banner">
                {shared_data['promo banner']}
                </div>
                <div class="divider"></div>
                <h3>CLIENT INFO</h3>
                <p>{shared_data['basic client info']}</p>
                <div class="divider"></div>
                <p style="color: grey;"><i>Click <a href="https://igaitools.com/commands-list/" style="color: grey;">here</a> for email customization options and other commands.</i></p>
                <div class="footer-logo">
                    <img src="https://i.imgur.com/imx182M.png" alt="Advise AI Logo" class="footer-logo-light" style="display: block;">
                    <img src="https://i.imgur.com/zbnAAvg.png" alt="Advise AI Logo Dark" class="footer-logo-dark" style="display: none;">
                </div>
            </div>
        </body>
        </html>
        """

        html_str = shared_data['final output']

        # the remainder of this function appends additional html content to the string above (e.g. documents, contact info)

        # convert shared_data['suggested funds'] to a dictionary
        if shared_data['suggested funds'] != "N/A":
            if shared_data['suggested funds'] != "Tell client that advisor will look into some options and get back to them.":
                try:
                    funds_dict = ast.literal_eval(shared_data['suggested funds'])
                    #pull name of recommended fund
                    fund_name = funds_dict["Fund Name"]

                    funds_html = {
                    "IG Mackenzie Global Science & Technology Fund": '<a href="https://factsheets.lipperweb.com/digital/invgrp/68221793_en.pdf">IG Mackenzie Global Science & Technology Fund</a>',
                    "Mackenzie Emerging Markets Fund": '<a href="https://www.mackenzieinvestments.com/content/dam/mackenzie/en/mackenzie-fundprofiles/fundprofile-emerging-markets-fund-f-05505-en.pdf">Mackenzie Emerging Markets Fund</a>',
                    "Mackenzie Unconstrained Fixed Income Fund": '<a href="https://www.mackenzieinvestments.com/content/dam/mackenzie/en/mackenzie-fundprofiles/fundprofile-unconstrained-fixed-income-fund-f-04765-en.pdf">Mackenzie Unconstrained Fixed Income Fund</a>',
                    "IG FI Canadian Equity Fund": '<a href="https://factsheets.lipperweb.com/digital/invgrp/68221710_en.pdf">IG FI Canadian Equity Fund</a>',
                    "Mackenzie International Dividend Fund": '<a href="https://www.mackenzieinvestments.com/content/dam/mackenzie/en/mackenzie-fundprofiles/fundprofile-international-dividend-fund-f-08013-en.pdf">Mackenzie International Dividend Fund</a>',
                    "IG Mackenzie Mutual of Canada": '<a href="https://factsheets.lipperweb.com/digital/invgrp/68221601_en.pdf">IG Mackenzie Mutual of Canada</a>',
                    "IG Mackenzie Canadian Corporate Bond Fund": '<a href="https://factsheets.lipperweb.com/digital/invgrp/68221692_en.pdf">IG Mackenzie Canadian Corporate Bond Fund</a>',
                    "iProfile U.S. Equity Private Pool": '<a href="https://factsheets.lipperweb.com/digital/invgrp/68020597_en.pdf">iProfile U.S. Equity Private Pool</a>',
                    "Mackenzie Ivy European Fund": '<a href="https://www.mackenzieinvestments.com/content/dam/mackenzie/en/mackenzie-fundprofiles/fundprofile-ivy-european-fund-f-08445-en.pdf">Mackenzie Ivy European Fund</a>',
                    "Mackenzie Maximum Diversification Global Multi-Asset Fund": '<a href="https://www.mackenzieinvestments.com/content/dam/mackenzie/en/mackenzie-fundprofiles/fundprofile-maximum-diversification-global-multi-asset-fund-f-09342-en.pdf">Mackenzie Maximum Diversification Global Multi-Asset Fund</a>',
                    "Mackenzie Northleaf Global Private Equity Fund": '<a href="https://www.mackenzieinvestments.com/content/dam/mackenzie/en/northleaf/fp-advisor-mackenzie-northleaf-global-private-equity-fund-en.pdf">Mackenzie Northleaf Global Private Equity Fund</a>',
                    "IG Mackenzie Global Precious Metals Fund": '<a href="https://factsheets.lipperweb.com/digital/invgrp/68759585_en.pdf">IG Mackenzie Global Precious Metals Fund</a>'
                    }

                    if fund_name in funds_html:
                        if shared_data['relevant attachments'] == "N/A":
                            shared_data['relevant attachments'] = shared_data['relevant attachments'].replace("N/A", "").strip()
                            shared_data['relevant attachments'] = shared_data['relevant attachments'] + funds_html[fund_name]
                        else:
                            shared_data['relevant attachments'] = shared_data['relevant attachments'] + "<br><br>" + funds_html[fund_name]

                except (ValueError, SyntaxError) as e:
                    print(f"Error converting string to dictionary: {e}")
            
        # if there are relevant attachements and/or suggested experts, appends the appropriate html content    
        condition_code_pairs = [
            (shared_data['relevant attachments'] != "N/A", f"""
            <h3>DOCUMENTS</h3>
            <p>{shared_data['relevant attachments']}</p>
            <div class="divider"></div>
            """
             ),
             (shared_data['suggested experts'] != "N/A", f"""
            <h3>EXPERT CONTACTS</h3>
            <p>{shared_data['suggested experts']}</p>
            <div class="divider"></div>
            """
             )
        ]

        for condition, code_to_insert in condition_code_pairs:
            if condition:
                insertion_point = html_str.rfind('<h3>CLIENT INFO</h3>')
                if insertion_point != -1:
                    html_str = html_str[:insertion_point] + code_to_insert + html_str[insertion_point:]

        # Update the shared_data with the modified HTML string
        shared_data['final output'] = html_str
        print("Final output prepared.")

    threads = [
        threading.Thread(target=task2),
        threading.Thread(target=task3),
        threading.Thread(target=task4),
        threading.Thread(target=task5),
        threading.Thread(target=task6),
        threading.Thread(target=task7),
        threading.Thread(target=task8),
        threading.Thread(target=task9),
        threading.Thread(target=task10),
        threading.Thread(target=task11)
    ]

    # Start threads
    for thread in threads:
        thread.start()

    # Wait for all threads to complete
    for thread in threads:
        thread.join()

    return shared_data['final output']

def get_sales_opps(subject):
    '''
    This function carries out the appropriate processing (both chatGPT and non-LLM) to generate html content for the 'opps' command.
    '''
    name = subject.split(':')[1].strip().lower()
    if name == "tim wilson":
        profile = tim
    elif name == "ethan brown":
        profile = ethan
    elif name == "olivia bennet":
        profile = olivia
    elif name == "natasha davis":
        profile = natasha
    else:
        return f"Error: Client not recognized.\n\nPlease sign off as Olivia, Ethan, Tim, or Natasha - these are the clients currently in the client database."
    
    if profile['context']["Percentage of portfolio allocated to fixed-income"] >= 0.7:
        portfolio_risk = 1
    elif profile['context']["Percentage of portfolio allocated to fixed-income"] >= 0.5:
        portfolio_risk = 2
    elif profile['context']["Percentage of portfolio allocated to fixed-income"] >= 0.3:
        portfolio_risk = 3    
    elif profile['context']["Percentage of portfolio allocated to fixed-income"] > 0.1:
        portfolio_risk = 4
    else:
        portfolio_risk = 5

    risk_profile_mapping = {
        "Very conservative": 1,
        "Conservative": 2,
        "Moderate": 3,
        "Aggressive": 4,
        "Very aggressive": 5
    }
    risk_profile = profile['brief']["Risk profile"]
    risk_profile_value = risk_profile_mapping.get(risk_profile)

    balance_rec = ""  
    if risk_profile_value > portfolio_risk:
        balance_rec = f"""
                        <div class="category">1. Portfolio Rebalancing</div>
                        <div class="rationale">Given client's desired risk profile is {risk_profile} and {str(shared_data['client profile']['context']['Percentage of portfolio allocated to fixed-income']*100)+'%'} of their portfolio is allocated to fixed-income, client should rebalance portfolio to include more equity holdings. <a style="color: grey;" href="https://www.mackenzieinvestments.com/en/investments/by-asset-class/equities?selectedGroup=mutual-fund">Learn more</a>.</div>
                        <br>
                        """

    compiled_recs = ""
    if balance_rec != "":
        compiled_recs += balance_rec
        x = 2
    else:
        x = 1

    prompt_sales = f"Client profile:\n\n{profile['context']}"
    bot_output_profileopps = execute_layer(prompt_sales,determine_salesopps)
    bot_output_profileopps = json.loads(bot_output_profileopps)

    reference = {
        "private asset funds": {
            "name": "Private Asset Funds",
            "link": "https://www.mackenzieinvestments.com/en/investments/by-asset-class/private-markets"
        },
        "term life insurance": {
            "name": "Term Life Insurance",
            "link": "https://www.canadalife.com/insurance/life-insurance/term-life-insurance.html?cpcsource=google&cpcmedium=cpc&cpccampaign=CL_BRAND_PROTECT_TERM_S_EN&adgroup=BRANDED&gad_source=1&gclid=Cj0KCQjwv7O0BhDwARIsAC0sjWOh33BwFUd8Y0ScH9xLgvRc_y3zHqhbjLjH4i837IgekM7NyZYpYDUaAt4qEALw_wcB"
        },
        "whole life insurance": {
            "name": "Whole Life Insurance",
            "link": "https://www.canadalife.com/insurance/life-insurance/permanent-life-insurance.html"
        },
        "par-whole life insurance": {
            "name": "Par-whole Life Insurance",
            "link": "https://www.canadalife.com/insurance/life-insurance/permanent-life-insurance/participating-whole-life-insurance.html?cpcsource=google&cpcmedium=cpc&cpccampaign=FALL_BRAND_PROTECT_2022_CA_B-M_S_EN_PBM&gad_source=1&gclid=Cj0KCQjwv7O0BhDwARIsAC0sjWNsNvE3-hHTSgOiWTpqA66wvZXl5QOYi9k0ia5GgSxpcL1Psv-74mIaAhxaEALw_wcB"
        },
        "disability and critical illness insurance": {
            "name": "Disability & Critical Illness Insurance",
            "link": "https://www.canadalife.com/blog/insurance/disability-vs-critical-illness-insurance-whats-the-difference.html"
        },
        "creditor insurance": {
            "name": "Creditor Insurance",
            "link": "https://www.nesto.ca/mortgage-basics/what-is-mortgage-loan-insurance-aka-mortgage-default-insurance/"
        },
         "mortgage": {
            "name": "Mortgage",
            "link": "https://www.nesto.ca/"
        }
    }

    for i, (product_key, rationale) in enumerate(bot_output_profileopps.items(), start=x):
        if product_key in reference:
            product_info = reference[product_key]
            compiled_recs += f"""
                <div class="category">{i}. {product_info['name']}</div>
                <div class="rationale">{rationale} <a style="color: grey;" href="{product_info['link']}">Learn more</a>.</div>
                <br>
                """
            
    client_brief = "<br>".join([f"{key}: {value}" for key, value in profile['brief'].items()])

    sales_output = f"""
        <html>
        <head>
            <style>
            body {{
                font-family: Arial, sans-serif;
                color: #333333;
                background-color: #ffffff;
                padding: 0px;
                font-size: 0.9em; /* Slightly smaller text */
            }}
            .email-container {{
                background-color: #ffffff;
                padding: 5px;
            }}
            .category {{
                font-weight: bold;
                color: #000000;
                position: relative;
                z-index: 2;
                font-size: 0.9em; /* Slightly smaller text */
            }}
            .rationale {{
                margin-top: 10px;
                margin-bottom: 5px;
                color: #000000; /* Changed rationale text to black */
                font-size: 0.9em; /* Slightly smaller text */
            }}
            h3 {{
                color: #2a52be; /* Darker blue color */
                font-family: 'Open Sans', sans-serif; /* Open Sans Bold font */
                font-weight: 700;
                font-size: 1.1em; /* Slightly smaller text */
            }}
            p {{
                line-height: 1.5;
                font-size: 0.9em; /* Slightly smaller text */
            }}
            .divider {{
                border-top: 1px solid #cccccc;
                margin: 20px 0;
            }}
            .footer-logo {{
                display: flex;
                justify-content: center;
                align-items: center;
                height: 25px;
                padding: 15px 0;
                background-color: #FFFFFF;
            }}
            .footer-logo img {{
                width: 120px;
                height: auto;
            }}
            @media (prefers-color-scheme: dark) {{
                .footer-logo-light {{
                    display: none !important;
                }}
                .footer-logo-dark {{
                    display: block !important;
                }}
            }}
            @media (prefers-color-scheme: light) {{
                .footer-logo-light {{
                    display: block !important;
                }}
                .footer-logo-dark {{
                    display: none !important;
                }}
            }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <h3>OPPORTUNITIES: {profile['context']['Client name']}</h3>
                {compiled_recs}
                <div class="divider"></div>
                <h3>CLIENT INFO</h3>
                <p>{client_brief}</p>
                <div class="divider"></div>
                <div class="footer-logo">
                    <img src="https://i.imgur.com/imx182M.png" alt="Advise AI Logo" class="footer-logo-light" style="display: block;">
                    <img src="https://i.imgur.com/zbnAAvg.png" alt="Advise AI Logo Dark" class="footer-logo-dark" style="display: none;">
                </div>
            </div>
        </body>
        </html>
        """

    print(sales_output)
    return sales_output

def handle_reply(body,from_address):
    '''
    This function does the processing for reply commands.
    '''
    words = body.split()
    if words:
        if words[0].lower() == "book":
            command_output = meeting_command(from_address)
        else:
            # selecting email 1
            if words[0].lower() == "1ldet":
                shared_data[from_address]['most recent reply'] = execute_layer(shared_data[from_address]['email 1'],remove_detail)
                print("Command: Removing detail from email 1.")

            elif words[0].lower() == "1mdet":
                prompt_moredetail = f"Question:\n\n{shared_data[from_address]['concise question']}\n\nEmail:\n\n{shared_data[from_address]['email 1']}\n\nAdditional info (if any):\n\n{shared_data[from_address]['all retrieved content']}"
                shared_data[from_address]['most recent reply'] = execute_layer(prompt_moredetail,add_detail)
                print("Command: adding detail to email 1.")

            elif words[0].lower() == "1cas":
                shared_data[from_address]['most recent reply'] = execute_layer(shared_data[from_address]['email 1'],more_casual)
                print("Command: Making email 1 more casual.")

            elif words[0].lower() == "1fri":
                shared_data[from_address]['most recent reply'] = execute_layer(shared_data[from_address]['email 1'],make_friendly)
                print("Command: Making email 1 more friendly.")

            elif words[0].lower() == "1pro":
                shared_data[from_address]['most recent reply'] = execute_layer(shared_data[from_address]['email 1'],make_professional)
                print("Command: Making email 1 more professional.")

            elif words[0].lower() == "1tran":
                shared_data[from_address]['most recent reply'] = execute_layer(shared_data[from_address]['email 1'],translate)
                print("Command: Translating email 1.")

            #selecting email 2
            elif words[0].lower() == "2ldet":
                shared_data[from_address]['most recent reply'] = execute_layer(shared_data[from_address]['email 2'],remove_detail)
                print("Command: Removing detail from email 2.")

            elif words[0].lower() == "2mdet":
                prompt_moredetail = f"Question:\n\n{shared_data[from_address]['concise question']}\n\nEmail:\n\n{shared_data['email 2']}\n\nAdditional info (if any):\n\n{shared_data[from_address]['all retrieved content']}"
                shared_data[from_address]['most recent reply'] = execute_layer(prompt_moredetail,add_detail)
                print("Command: adding detail to email 2.")

            elif words[0].lower() == "2cas":
                shared_data[from_address]['most recent reply'] = execute_layer(shared_data[from_address]['email 2'],more_casual)
                print("Command: Making email 2 more casual.")

            elif words[0].lower() == "2fri":
                shared_data[from_address]['most recent reply'] = execute_layer(shared_data[from_address]['email 2'],make_friendly)
                print("Command: Making email 2 more friendly.")

            elif words[0].lower() == "2pro":
                shared_data[from_address]['most recent reply'] = execute_layer(shared_data[from_address]['email 2'],make_professional)
                print("Command: Making email 2 more professional.")
            
            elif words[0].lower() == "2tran":
                shared_data[from_address]['most recent reply'] = execute_layer(shared_data[from_address]['email 2'],translate)
                print("Command: Translating email 2.")

            # no email selection
            elif words[0].lower() == "meet":
                shared_data[from_address]['most recent reply'] = execute_layer(shared_data[from_address]['original inquiry'],schedule_meeting_instead)
                print("Command: Offering to schedule meeting instead.")

            elif words[0].lower() == "custom:":
                colon_index = body.find(":")
                instructions = body[colon_index + 1:]
                prompt_customchanges = f"Email:{shared_data[from_address]['email 1']}\n\nInstructions:{instructions}"
                shared_data[from_address]['most recent reply'] = execute_layer(prompt_customchanges,change_custom)
                print("Command: Adjusting email 1 based on custom request.")

            # commands after command
            elif words[0].lower() == "ldet":
                if shared_data[from_address]['most recent reply'] != None:
                    shared_data[from_address]['most recent reply'] = execute_layer(shared_data[from_address]['most recent reply'],remove_detail)
                    print("Command: Removing detail most recent draft.")
                else:
                    print("Invalid command")
                    return "Invalid command."

            elif words[0].lower() == "mdet":
                if shared_data[from_address]['most recent reply'] != None:
                    prompt_moredetail = f"Question:\n\n{shared_data[from_address]['concise question']}\n\nEmail:\n\n{shared_data[from_address]['most recent reply']}\n\nAdditional info (if any):\n\n{shared_data[from_address]['all retrieved content']}"
                    shared_data[from_address]['most recent reply'] = execute_layer(prompt_moredetail,add_detail)
                    print("Command: Adding detail to most recent draft.")
                else:
                    print("Invalid command")
                    return "Invalid command."
                
            elif words[0].lower() == "cas":
                if shared_data[from_address]['most recent reply'] != None:
                    shared_data[from_address]['most recent reply'] = execute_layer(shared_data[from_address]['most recent reply'],more_casual)
                    print("Command: Making most recent draft more casual.")
                else:
                    print("Invalid command")
                    return "Invalid command."

            elif words[0].lower() == "fri":
                if shared_data[from_address]['most recent reply'] != None:
                    shared_data[from_address]['most recent reply'] = execute_layer(shared_data[from_address]['most recent reply'],make_friendly)
                    print("Command: Making most recent draft more friendly.")
                else:
                    print("Invalid command")
                    return "Invalid command."

            elif words[0].lower() == "pro":
                if shared_data[from_address]['most recent reply'] != None:
                    shared_data[from_address]['most recent reply'] = execute_layer(shared_data[from_address]['most recent reply'],make_professional)
                    print("Command: Making most recent draft more professional")
                else:
                    print("Invalid command")
                    return "Invalid command."
            
            elif words[0].lower() == "tran":
                if shared_data[from_address]['most recent reply'] != None:
                    shared_data[from_address]['most recent reply'] = execute_layer(shared_data[from_address]['most recent reply'],translate)
                    print("Command: Translating most recent draft")
                else:
                    print("Invalid command")
                    return "Invalid command."

            else:
                print("Command not recognized.")
                return "Command not recognized."
            
            html_formatted_reply = shared_data[from_address]['most recent reply'].replace('\n', '<br>')

            command_output = f"""
                <html>
                <head>
                    <style>
                    body {{
                        font-family: Arial, sans-serif;
                        color: #333333;
                        background-color: #ffffff;
                        padding: 20px;
                        font-size: 0.9em
                    }}
                    h3 {{
                        color: #2a52be; /* Darker blue color */
                    }}
                    p {{
                        line-height: 1.5;
                        font-size: 0.9em;
                    }}
                    .footer-logo {{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 25px;
                    padding: 15px 0;
                    background-color: #FFFFFF;
                    }}
                    .footer-logo img {{
                        width: 120px;
                        height: auto;
                    }}
                    @media (prefers-color-scheme: dark) {{
                    .footer-logo-light {{
                        display: none !important;
                    }}
                    .footer-logo-dark {{
                        display: block !important;
                    }}
                    }}
                    @media (prefers-color-scheme: light) {{
                        .footer-logo-light {{
                            display: block !important;
                        }}
                        .footer-logo-dark {{
                            display: none !important;
                        }}
                    }}
                    </style>
                </head>
                <body>
                    <div class="email-container">
                    <p>{html_formatted_reply}</p>
                    <hr>
                    <p style="color: grey;"><i>
                    For further adjustment:</p>
                        <li style="color: grey; font-size: 0.9em"><strong>meet</strong> = suggest to schedule a meeting rather than addressing the inquiry via email</li>
                        <li style="color: grey; font-size: 0.9em"><strong>cas</strong> = make reply more casual</li>
                        <li style="color: grey; font-size: 0.9em"><strong>pro</strong> = make reply more professional</li>
                        <li style="color: grey; font-size: 0.9em"><strong>fri</strong> = make reply more friendly</li>
                        <li style="color: grey; font-size: 0.9em"><strong>mdet</strong> = make reply more detailed</li>
                        <li style="color: grey; font-size: 0.9em"><strong>ldet</strong> = make reply less detailed</li>
                        <li style="color: grey; font-size: 0.9em"><strong>tran</strong> = translate reply to French</li>
                        <li style="color: grey; font-size: 0.9em"><strong>custom: [your instructions]</strong> = adjust reply with your own instructions</li>
                    </i></p>
                    <hr><br>
                    <div class="footer-logo">
                        <img src="https://i.imgur.com/imx182M.png" alt="Advise AI Logo" class="footer-logo-light" style="display: block;">
                        <img src="https://i.imgur.com/zbnAAvg.png" alt="Advise AI Logo Dark" class="footer-logo-dark" style="display: none;">
                    </div>
                    </div>
                </body>
                </html>
            """

        return command_output
    else: 
        print("Reply empty.")

def meeting_command(from_address):
    '''
    This function does the processing for the 'book' command.
    '''
    today = date.today().strftime("%A, %B %d, %Y") 
    details = execute_layer(f"Today is {today}\n\nClient's email:\n\n{shared_data[from_address]['original inquiry']}\n\nAdvisor Response:\n\n{shared_data[from_address]['email 1']}\n\nDriving Times:\n\nTo restaurant for lunch (with current traffic): {shared_data['l_drive_time_traffic']}\nTo restaurant for dinner (with current traffic): {shared_data['d_drive_time_traffic']}",determine_meeting_time)
            
    details = json.loads(details)

    print(details)

    summary = details['title']
    start_datetime = details['start_datetime']
    end_datetime = details['end_datetime']
    description = details['description']
    location = details['location']

    #creates a calendar event for the meeting
    schedule_meeting(summary,location,description,start_datetime,end_datetime)

    if location == 'Ferriera Cafe':
        driving_time = shared_data['l_drive_time_traffic']
    if location == 'Estiatorio Milos Montreal':
        driving_time = shared_data['d_drive_time_traffic']
    
    # if the meeting is at a restaurant, uses the driving time (calculated earlier) to determine the start and end times of 2 additional events representing travel time
    if location == 'Ferriera Cafe' or location == 'Estiatorio Milos Montreal':
        minutes = int(re.search(r'\d+', driving_time).group())
        dt = datetime.fromisoformat(start_datetime[:-6])
        new_dt = dt - timedelta(minutes=minutes)
        timezone_offset = start_datetime[-6:]
        starttime_driveto = new_dt.strftime('%Y-%m-%dT%H:%M:%S') + timezone_offset
        endtime_driveto = start_datetime

        dt = datetime.fromisoformat(end_datetime[:-6])
        new_dt = dt + timedelta(minutes=minutes)
        starttime_driveback = end_datetime
        endtime_driveback = new_dt.strftime('%Y-%m-%dT%H:%M:%S') + timezone_offset

        # schedules events for 'travel time'
        schedule_meeting(f"[Travel time]", None, None,starttime_driveto,endtime_driveto)
        schedule_meeting(f"[Travel time]", None, None,starttime_driveback,endtime_driveback)

    # html string for body of confirmation email:
    output = f"""
            <html>
            <head>
                <style>
                body {{
                    font-family: Arial, sans-serif;
                    color: #333333;
                    background-color: #ffffff;
                    padding: 20px;
                    font-size: 0.9em
                }}
                h3 {{
                    color: #2a52be; /* Darker blue color */
                }}
                p {{
                    line-height: 1.5;
                    font-size: 0.9em;
                }}
                 .footer-logo {{
                display: flex;
                justify-content: center;
                align-items: center;
                height: 25px;
                padding: 15px 0;
                background-color: #FFFFFF;
                }}
                .footer-logo img {{
                    width: 120px;
                    height: auto;
                }}
                @media (prefers-color-scheme: dark) {{
                .footer-logo-light {{
                    display: none !important;
                }}
                .footer-logo-dark {{
                    display: block !important;
                }}
                }}
                @media (prefers-color-scheme: light) {{
                    .footer-logo-light {{
                        display: block !important;
                    }}
                    .footer-logo-dark {{
                        display: none !important;
                    }}
                }}
                </style>
            </head>
            <body>
                <div class="email-container">
                <p>Meeting with {shared_data['client profile']['context']['Client name']} added to calendar.</p>
                <br><hr><br>
                <div class="footer-logo">
                    <img src="https://i.imgur.com/imx182M.png" alt="Advise AI Logo" class="footer-logo-light" style="display: block;">
                    <img src="https://i.imgur.com/zbnAAvg.png" alt="Advise AI Logo Dark" class="footer-logo-dark" style="display: none;">
                </div>
                </div>
            </body>
            </html>
        """
              
    return output

def recognize_client_function(body):
    '''
    Recognizes the client based on how the email is signed off and fetches their client profile.
    '''
    name = execute_layer(body,recognize_client).strip().lower()
        
    if name == "tim":
        shared_data['client profile'] = tim
        return "Client recognized"
    elif name == "ethan":
        shared_data['client profile'] = ethan
        return "Client recognized"
    elif name == "olivia":
        shared_data['client profile'] = olivia
        return "Client recognized"
    elif name == "natasha":
        shared_data['client profile'] = natasha
        return "Client recognized"
    else:
        print(f"Error: Client not recognized.\n\nPlease sign off as Olivia, Ethan, Tim, or Natasha - these are the clients currently in the client database.")
        return f"Error: Client not recognized.\n\nPlease sign off as Olivia, Ethan, Tim, or Natasha - these are the clients currently in the client database."


# connecting to database and creating table (for logging interactions with assistant)
conn = sqlite3.connect('interaction_logs.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT,
    inquiry TEXT,
    interaction_time TEXT,
    processing_time REAL,
    response_html TEXT
)
''')
conn.commit()

# logs relevant info and html response for an interaction with the assistant
def log_interaction(sender, inquiry, response_html, processing_time):
    utc_time = datetime.now(pytz.utc)
    eastern = pytz.timezone('US/Eastern')
    eastern_time = utc_time.astimezone(eastern)
    interaction_time = eastern_time.isoformat()

    cursor.execute('''
    INSERT INTO interactions (sender, inquiry, interaction_time, processing_time, response_html)
    VALUES (?, ?, ?, ?, ?)
    ''', (sender, inquiry, interaction_time, processing_time, response_html))
    conn.commit()

def main():
    global shared_data
    while True:
        shared_data = load_shared_data()
        print("Checking for recent email...")
        try:
            recent_email = read_recent_email()
        except Exception as e:
            print(f"Error reading recent email: {e}")
            time.sleep(10)
            continue

        if recent_email:
            from_address, subject, body = recent_email
            # if this is the user's first time using the assistant, it initializes a places for their generated content to be stores in the shared_data file
            if from_address not in shared_data:
                shared_data[from_address] = {}
            # timer for measuring processing time
            start_time = time.time()


            # feeds email body to one of the processing functions, depending on the subject
            if subject.lower().startswith("re:"):
                output = handle_reply(body,from_address)
            elif subject.lower().startswith("opps:"):
                output = get_sales_opps(subject)
            elif subject.lower().startswith("book"):
                output = meeting_command(from_address)
            else:
                shared_data[from_address]['original inquiry'] = body
                client_verdict = recognize_client_function(body)
                if client_verdict == "Client recognized":
                    output = llm(subject + "\n\n" + body,from_address)
                else:
                    output = client_verdict
            try:
                    send_email(from_address, subject, output)
                    end_time = time.time()
                    processing_time = round(end_time - start_time,2)
                    log_interaction(from_address,body,output,processing_time)
                    print(f"Time to process: {processing_time} seconds")
            except Exception as e:
                print(f"Error sending email: {e}")

        save_shared_data(shared_data)
        # waits 10 seconds before checking for new emails again
        time.sleep(10)

if __name__ == "__main__":
    main()