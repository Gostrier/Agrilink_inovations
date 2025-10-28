# mpesa_gateway.py
import requests
import base64
from datetime import datetime
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class MpesaGateway:
    def __init__(self):
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.shortcode = settings.MPESA_SHORTCODE   # Your shortcode (Paybill/Till)
        self.passkey = settings.MPESA_PASSKEY
        self.base_url = "https://sandbox.safaricom.co.ke"  # Change to production when live

    def authenticate(self):
        """Get OAuth token from Safaricom"""
        url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        try:
            response = requests.get(url, auth=(self.consumer_key, self.consumer_secret))
            response.raise_for_status()
            return response.json().get("access_token")
        except Exception as e:
            logger.error(f"M-Pesa Authentication Failed: {e}")
            return None

    def stk_push(self, phone, amount=10, account_reference="ACCESS-FEE"):
        """
        Trigger STK Push to customer phone for flat fee (default 10 KES).
        """
        access_token = self.authenticate()
        if not access_token:
            return {"error": "Authentication failed. Check credentials."}

        url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password = base64.b64encode((self.shortcode + self.passkey + timestamp).encode()).decode("utf-8")

        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),        # Always 10 unless overridden
            "PartyA": str(phone),         # Customer phone
            "PartyB": self.shortcode,     # Your shortcode (Paybill/Till)
            "PhoneNumber": str(phone),    # Customer phone
            "CallBackURL": settings.MPESA_CALLBACK_URL,
            "AccountReference": account_reference,
            "TransactionDesc": "Access Farmer Listing",
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"M-Pesa STK Push Failed: {e}")
            return {"error": "STK push request failed."}
