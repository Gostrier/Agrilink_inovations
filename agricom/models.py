from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal
class Note(models.Model):
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to="notes/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notes")

    # ✅ New field for storing cached AI report
    cached_ai_report = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

    def is_pdf(self):
        return self.file.name.lower().endswith(".pdf")

    def is_text(self):
        return self.file.name.lower().endswith((".txt", ".md"))

    def is_docx(self):
        return self.file.name.lower().endswith(".docx")

    def is_image(self):
        return self.file.name.lower().endswith((".png", ".jpg", ".jpeg"))


class Farmer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, unique=True)
    location = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - Farmer"


class Buyer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return f"{self.user.username} - Buyer"


class Listing(models.Model):
    ROLE_CHOICES = [
        ('farmer', 'Farmer Listing'),
        ('buyer', 'Buyer Request'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    quantity = models.IntegerField(null=True, blank=True)
    buyer_phone = models.CharField(max_length=15, blank=True, null=True)  # only for buyer listings
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.role}) - {self.user.username}"

class Transaction(models.Model):
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    mpesa_receipt = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("success", "Success"), ("failed", "Failed")],
        default="pending"
    )
    commission = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_commission(self):
        """5% commission for platform"""
        return self.amount * Decimal("0.05")

    def save(self, *args, **kwargs):
        if not self.commission:
            self.commission = self.calculate_commission()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Txn {self.id} - {self.status}"


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=12)  # 2547XXXXXXXX
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=10.00)  # Always 10 KES
    checkout_request_id = models.CharField(max_length=100, blank=True, null=True)
    mpesa_receipt_number = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=50, default="Pending")  # Pending, Success, Failed
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.amount} - {self.status}"

class SoilTest(models.Model):
    image = models.ImageField(upload_to="soil_tests/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="soil_tests")
    ai_result = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Soil Test by {self.uploaded_by.username} at {self.uploaded_at}"


class CropDisease(models.Model):
    image = models.ImageField(upload_to="crop_diseases/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="crop_diseases")
    ai_result = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Crop Disease Report by {self.uploaded_by.username} at {self.uploaded_at}"

class BuyerListingDetail(models.Model):
    listing = models.OneToOneField('Listing', on_delete=models.CASCADE, related_name='buyer_detail')
    phone = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.listing.title} - {self.phone}"        