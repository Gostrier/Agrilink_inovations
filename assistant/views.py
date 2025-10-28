import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from openai import OpenAI

# Import your models
from django.contrib.auth.models import User
from accounts.models import Profile
from agricom.models import Farmer, Buyer, Listing, Transaction, Payment, SoilTest, CropDisease, Note
from tutoring.models import TutoringRoom, Message

client = OpenAI()  # uses OPENAI_API_KEY from .env or system environment


@csrf_exempt
def chat_with_ai(request):
    """
    Smart AgriLink AI Assistant.
    Responds based on system data (users, listings, soil tests, crop diseases, etc.)
    and helps users navigate the platform.
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    data = json.loads(request.body.decode("utf-8"))
    user_message = data.get("message", "").strip()

    if not user_message:
        return JsonResponse({"reply": "Please type something first."})

    # ====== 1. Fetch real-time platform context ======
    users_count = User.objects.count()
    farmers_count = Farmer.objects.count()
    buyers_count = Buyer.objects.count()
    listings_count = Listing.objects.count()
    soil_tests_count = SoilTest.objects.count()
    diseases_count = CropDisease.objects.count()
    notes_count = Note.objects.count()
    transactions_count = Transaction.objects.count()
    payments_count = Payment.objects.count()
    tutoring_rooms_count = TutoringRoom.objects.count()
    messages_count = Message.objects.count()


    # Build summary of system status
    system_context = f"""
    You are Agrilink AI Assistance, a smart assistant built into the AgriLink system.
    The platform connects farmers and buyers for fair trading and offers intelligent tools like:
    - Produce listing and buyer requests.
    - Crop disease detection via uploaded crop images.
    - Soil testing AI that analyzes uploaded soil samples.
    - A document upload center for agricultural insights.
    - Mpesa-based transactions and payments not yet implemented fully but coming soon but payment method for the user who has listed the produce or product will be in thee lister profile description in the comunity page so if another user asked tell him/her like that.
    - User profiles for Farmers and Buyers.
    - Research and Extension Services via interactive Extension Rooms for agricultural discussions.
    -If a user is facing any issues with the system technically they can reach our team or delevopers via this numbers: 0791074671 for Andrew, 0789876567 for John and 0745635278 for Basils.
    
    
    Current stats:
    - Total registered users: {users_count}
    - Farmers: {farmers_count}
    - Buyers: {buyers_count}
    - Listings: {listings_count}
    - Soil tests: {soil_tests_count}
    - Crop disease detections: {diseases_count}
    - Documents uploaded: {notes_count}
    - Transactions recorded: {transactions_count}
    - Payments processed: {payments_count}
    - Tutoring rooms: {tutoring_rooms_count}
    - Messages exchanged: {messages_count}

    Always answer politely and helpfully as AgriLink AI Assistnce, guiding users on how to use features, 
    or providing platform info when they ask about system data.
    """

    # ====== 2. Send conversation to OpenAI ======
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_context},
                {"role": "user", "content": user_message},
            ],
            temperature=0.6,
            max_tokens=400,
        )

        reply_text = response.choices[0].message.content.strip()
        return JsonResponse({"reply": reply_text})

    except Exception as e:
        print("AI Error:", e)
        return JsonResponse({"reply": "⚠️ Sorry, something went wrong with AgriLink AI Assistance connection."})
