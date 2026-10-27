import os
import requests
import stripe
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY

# Define your prices here
PRICES = {
    "starter": "price_1U17IjGdIMhULOta19MGBfW1",  # $25/month
    "pro": "price_1UBSZDGdIMhULOtacR1oAU9X"  # $497/month
}


@app.get("/api/news")
async def get_news(symbol: str = None, category: str = "general"):
    """Fetch market news from Finnhub. Pass ?symbol=AAPL for company news
    or ?category=crypto|forex|general|merger for market-wide news."""
    if not FINNHUB_API_KEY:
        return {"articles": [], "error": "News API not configured"}
    try:
        if symbol:
            today = datetime.now().strftime("%Y-%m-%d")
            week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            url = "https://finnhub.io/api/v1/company-news"
            params = {
                "symbol": symbol.upper(),
                "from": week_ago,
                "to": today,
                "token": FINNHUB_API_KEY,
            }
        else:
            url = "https://finnhub.io/api/v1/news"
            params = {"category": category, "token": FINNHUB_API_KEY}

        resp = requests.get(url, params=params, timeout=8)
        data = resp.json()
        articles = data[:10] if isinstance(data, list) else []
        return {
            "articles": [
                {
                    "headline": a.get("headline"),
                    "summary": a.get("summary"),
                    "source": a.get("source"),
                    "url": a.get("url"),
                    "datetime": a.get("datetime"),
                    "image": a.get("image"),
                }
                for a in articles
            ]
        }
    except Exception as e:
        return {"error": str(e), "articles": []}


@app.post("/api/create-checkout-session")
async def create_checkout_session(plan: str = "starter"):
    try:
        # Get the correct price ID based on the plan
        price_id = PRICES.get(plan, PRICES["starter"])  # Default to starter if invalid

        checkout_session = stripe.checkout.Session.create(
            mode="subscription",
            payment_method_types=["card"],
            line_items=[{
                "price": price_id,
                "quantity": 1,
            }],
            success_url="https://stock-bull-bearish.onrender.com/?success=true",
            cancel_url="https://stock-bull-bearish.onrender.com/?canceled=true",
        )
        return {"checkoutUrl": checkout_session.url}
    except Exception as e:
        return {"error": str(e)}


@app.get("/health")
async def health():
    return {"status": "healthy"}
