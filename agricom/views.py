from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Note,  SoilTest, CropDisease
from .forms import NoteForm, SoilTestForm, CropDiseaseForm
import PyPDF2
import docx
import extract_msg
import re
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Listing, Transaction, Buyer
from .mpesa import MpesaGateway
from .mpesa import MpesaGateway
from .models import Payment
from django.views.decorators.csrf import csrf_exempt
from .models import Listing
from urllib.parse import urlencode

from .models import Listing, BuyerListingDetail
from openai import OpenAI
import base64

# --- Utility function to clean AI results ---
def remove_emojis(text):
    """Remove emojis and non-ASCII characters (keeps plain text only)."""
    return re.sub(r'[^\x00-\x7F]+', '', text)



# ✅ Initialize OpenAI client for version 2.2.0
client = OpenAI()  # <-- Replace with your OpenAI key


# ---------------- NOTES / DOCUMENTS ----------------
def notes_upload(request):
    """Upload notes/documents (farm records, soil reports, crop history, etc.)"""
    if request.method == "POST":
        form = NoteForm(request.POST, request.FILES)
        if form.is_valid():
            note = form.save(commit=False)
            note.uploaded_by = request.user
            note.save()
            messages.success(request, "Document uploaded successfully!")
            return redirect("notes_list")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = NoteForm()
    return render(request, "notes_upload.html", {"form": form})


def notes_list(request):
    """List of uploaded farm-related documents"""
    notes = Note.objects.all().order_by("-uploaded_at")
    return render(request, "notes_list.html", {"notes": notes})


def extract_text_from_file(note):
    """Extract text content from PDF, DOCX, TXT, or MSG files"""
    content = ""
    try:
        if note.file.name.lower().endswith(".pdf"):
            with open(note.file.path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    content += page.extract_text() or ""
        elif note.file.name.lower().endswith(".txt"):
            with open(note.file.path, "r", encoding="utf-8") as f:
                content = f.read()
        elif note.file.name.lower().endswith(".docx"):
            doc = docx.Document(note.file.path)
            content = "\n".join([para.text for para in doc.paragraphs])
        elif note.file.name.lower().endswith(".msg"):
            msg = extract_msg.Message(note.file.path)
            msg_sender = msg.sender or ""
            msg_subject = msg.subject or ""
            msg_date = str(msg.date) or ""
            msg_body = msg.body or ""
            content = f"Sender: {msg_sender}\nSubject: {msg_subject}\nDate: {msg_date}\n\n{msg_body}"
        else:
            content = "Unsupported file type for extraction."
    except Exception as e:
        content = f"Error extracting text: {e}"
    return content


# ---------------- AI ANALYSIS HANDLER ----------------
def generate_answer(prompt, image_path=None):
    """Generate AI response using GPT-4o-mini for both text and image analysis."""
    try:
        messages = [{"role": "system", "content": "You are AgriLink AI, a smart agricultural assistant."}]
        if image_path:
            # Convert image to base64 for GPT-4o-mini analysis
            with open(image_path, "rb") as img_file:
                image_bytes = img_file.read()
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")

            messages.append({
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        }
                    }
                ]
            })
        else:
            messages.append({"role": "user", "content": prompt})

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        return response.choices[0].message.content
    except Exception as e:
        return f"Error during AI analysis: {e}"



def remove_emojis(text):
    """Clean out emojis and unwanted characters"""
    import re
    return re.sub(r"[^\w\s,.!?;:()\-\n]", "", text)


# ---------------- PREVIEW AND AI PROCESS ----------------
def preview_note(request, pk):
    """Preview uploaded file and run AI analysis (document, soil, or crop)."""
    note = get_object_or_404(Note, pk=pk)
    extracted_text = extract_text_from_file(note)
    ai_results = note.cached_ai_report

    if request.method == "POST":
        report_type = request.POST.get("report_type")
        prompt = None
        image_path = None

        if report_type == "doc":
            prompt = f"""
You are AgriAI, an intelligent assistant for farmers.
Analyze this document and give insights across 5 perspectives:
1. Production → best inputs, timing.
2. Protection → disease/pest alerts.
3. Post-harvest → pricing & storage.
4. Finance & Insurance → access to capital, risk.
5. Food Security → sustainability & yield impact.

Document:
{extracted_text}
"""
        elif report_type == "soil":
            prompt = """Analyze the uploaded soil image. Identify soil type, estimate pH, and recommend fertilizer or lime application. Give real, clear results."""
            image_path = note.file.path
        elif report_type == "crop":
            prompt = """Analyze this crop image. Identify visible diseases, symptoms, and suggest treatments or preventive measures. Provide practical farmer advice."""
            image_path = note.file.path

        if prompt:
            ai_results = generate_answer(prompt, image_path)
            if ai_results:
                clean_results = remove_emojis(ai_results)
                note.cached_ai_report = clean_results
                note.save()
                messages.success(request, f"{report_type.capitalize()} analysis completed!")

    context = {
        "note": note,
        "extracted_text": extracted_text,
        "ai_analysis": note.cached_ai_report,
    }
    return render(request, "preview_note.html", context)


# ---------------- PDF EXPORT ----------------
def download_ai_report(request, pk):
    """Download AI insights report as PDF"""
    note = get_object_or_404(Note, pk=pk)

    if not note.cached_ai_report:
        return HttpResponse("No AI report available. Please generate one first.")

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{note.title}_AI_Report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph("AI Agricultural Insights Report", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"<b>Document:</b> {note.title}", styles["Heading3"]))
    story.append(Spacer(1, 8))

    report_lines = note.cached_ai_report.split("\n")
    for line in report_lines:
        if line.strip():
            story.append(Paragraph(line.strip(), styles["Normal"]))
            story.append(Spacer(1, 6))

    doc.build(story)
    return response

@csrf_exempt
def initiate_payment(request):
    """Force KSh 10 payment before access"""
    if request.method == "POST":
        phone = request.POST.get("phone")
        amount = 10  # Always 10 shillings

        if not phone:
            return JsonResponse({"error": "Phone number is required"}, status=400)

        # Save initial payment record
        payment = Payment.objects.create(
            user=request.user,
            phone_number=phone,
            amount=amount
        )

        # Trigger STK Push (ensure live=True)
        gateway = MpesaGateway(live=True)
        result = gateway.stk_push(
            phone=phone,
            amount=int(amount),
            account_reference=f"ACCESS-{request.user.username}"
        )

        # Save CheckoutRequestID or error message
        checkout_id = (
            result.get("CheckoutRequestID")
            or result.get("errorMessage")
            or result.get("error")
        )
        payment.checkout_request_id = checkout_id
        payment.save()

        return JsonResponse(result, safe=False)

    return JsonResponse({"error": "POST request required"}, status=405)


@csrf_exempt
def mpesa_callback(request):
    """Handle M-Pesa STK callback (live)"""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            stk_callback = data.get("Body", {}).get("stkCallback", {})
            checkout_request_id = stk_callback.get("CheckoutRequestID")
            result_code = stk_callback.get("ResultCode")
            result_desc = stk_callback.get("ResultDesc")

            payment = Payment.objects.filter(checkout_request_id=checkout_request_id).first()
            if payment:
                if result_code == 0:
                    payment.status = "Success"
                    for item in stk_callback.get("CallbackMetadata", {}).get("Item", []):
                        if item.get("Name") == "MpesaReceiptNumber":
                            payment.mpesa_receipt_number = item.get("Value")
                            break
                else:
                    payment.status = f"Failed - {result_desc}"
                payment.save()
        except Exception as e:
            print(f"Callback error: {e}")
        return HttpResponse("Success")
    return HttpResponse("Only POST allowed")


def listing(request, listing_id):
    """Restrict farmer listing details until user has paid"""
    payment = Payment.objects.filter(user=request.user, status="Success").order_by("-created_at").first()
    if not payment:
        return redirect("payment_page")  # redirect to payment form

    listing = get_object_or_404(Listing, id=listing_id)
    return render(request, "listing_detail.html", {"listing": listing})



def delete_note(request, pk):
    """Delete a note (file)"""
    note = get_object_or_404(Note, pk=pk)
    
    # Ensure the user is the one who uploaded the note before allowing deletion
    if note.uploaded_by == request.user:
        note.delete()
        messages.success(request, "Note deleted successfully!")
    else:
        messages.error(request, "You are not authorized to delete this note.")
    
    return redirect('notes_list')







@login_required
def listing_page(request):
    listings = Listing.objects.all().order_by("-created_at")

    if request.method == "POST":
        role = request.POST.get("role")
        title = request.POST.get("title")
        description = request.POST.get("description")
        price = request.POST.get("price") if role == "farmer" else None  # ✅ buyers don't need price
        quantity = request.POST.get("quantity")
        phone = request.POST.get("phone")  # Only relevant if role == "buyer"

        listing = Listing.objects.create(
            user=request.user,
            role=role,
            title=title,
            description=description,
            price=price,
            quantity=quantity,
        )

        if role == "buyer" and phone:
            BuyerListingDetail.objects.create(listing=listing, phone=phone)

        messages.success(request, "Your listing has been posted successfully.")
        return redirect("listing_page")

    return render(request, "listing_page.html", {"listings": listings})


@login_required
def order_page(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    return render(request, "order_page.html", {"listing": listing})

@login_required
def buyer_available(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id, role="buyer")
    buyer_detail = getattr(listing, 'buyer_detail', None)

    if not buyer_detail:
        messages.error(request, "No phone number available for this buyer listing.")
        return redirect("listing_page")

    return render(request, "buyer_available.html", {
        "listing": listing,
        "buyer_phone": buyer_detail.phone
    })



@login_required
def buyer_not_available(request, listing_id):
    messages.info(request, "Kindly make produce for this buyer.")
    return redirect("listing_page")
    
def order_page(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    if request.method == "POST":
        quantity = int(request.POST.get("quantity", listing.quantity))
        total_price = quantity * listing.price
        request.session['order_quantity'] = quantity
        request.session['total_price'] = float(total_price)
        return redirect('payment_page', listing_id=listing.id)
    return render(request, 'order_page.html', {'listing': listing})

def payment_page(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    order_quantity = request.session.get('order_quantity', listing.quantity)
    total_price = request.session.get('total_price', listing.price * order_quantity)
    return render(request, 'payment_page.html', {
        'listing': listing,
        'order_quantity': order_quantity,
        'total_price': total_price
    })