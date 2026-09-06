import os
import stripe
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

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
    "pro": "price_1UBSZDGdIMhULOtacR1oAU9X"       # $497/month
}

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
