import requests
import base64
from datetime import datetime
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class MpesaGateway:
    def __init__(self, live=True):
        """Use live Safaricom environment"""
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.shortcode = settings.MPESA_SHORTCODE   # Your Paybill or Till number
        self.passkey = settings.MPESA_PASSKEY
        self.base_url = "https://api.safaricom.co.ke" if live else "https://sandbox.safaricom.co.ke"

    def authenticate(self):
        """Get OAuth token from Safaricom (Live)"""
        url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        try:
            response = requests.get(url, auth=(self.consumer_key, self.consumer_secret))
            response.raise_for_status()
            token = response.json().get("access_token")
            if not token:
                logger.error(f"No access token in response: {response.text}")
            return token
        except Exception as e:
            logger.error(f"M-Pesa Authentication Failed: {e}")
            return None

    def normalize_phone(self, phone):
        """Ensure phone is in format 2547XXXXXXXX"""
        phone = str(phone).strip()
        if phone.startswith("0"):
            phone = "254" + phone[1:]
        elif phone.startswith("+"):
            phone = phone[1:]
        return phone

    def stk_push(self, phone, amount=10, account_reference="ACCESS-FEE", transaction_desc="Access Farmers Listing"):
        """Trigger STK Push (Live)"""
        access_token = self.authenticate()
        if not access_token:
            return {"error": "Authentication failed. Check credentials."}

        url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password = base64.b64encode(
            (self.shortcode + self.passkey + timestamp).encode()
        ).decode("utf-8")

        phone = self.normalize_phone(phone)

        payload = {
            "BusinessShortCode": self.shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",  # Works for both Paybill & Till
            "Amount": int(amount),
            "PartyA": phone,
            "PartyB": self.shortcode,
            "PhoneNumber": phone,
            "CallBackURL": settings.MPESA_CALLBACK_URL,
            "AccountReference": account_reference,
            "TransactionDesc": transaction_desc,
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(f"STK Push HTTP {response.status_code}: {response.text}")
            return {
                "error": "STK push failed",
                "status_code": response.status_code,
                "details": response.text,
            }
        except Exception as e:
            logger.error(f"M-Pesa STK Push Exception: {e}")
            return {"error": "STK push request failed", "details": str(e)}
