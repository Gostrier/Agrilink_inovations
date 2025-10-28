from django.contrib import admin
from .models import Note, Farmer, Buyer, Listing, Transaction, Payment

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_by', 'uploaded_at', 'is_pdf', 'is_text')
    search_fields = ('title', 'uploaded_by__username')
    list_filter = ('uploaded_at',)

@admin.register(Farmer)
class FarmerAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'location')
    search_fields = ('user__username', 'phone', 'location')


@admin.register(Buyer)
class BuyerAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone')
    search_fields = ('user__username', 'phone')


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'role', 'price', 'quantity', 'created_at')
    search_fields = ('title', 'user__username', 'role')
    list_filter = ('role', 'created_at')
    ordering = ('-created_at',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'listing', 'amount', 'status', 'commission', 'created_at')
    search_fields = ('buyer__user__username', 'listing__title', 'mpesa_receipt')
    list_filter = ('status', 'created_at')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'amount', 'checkout_request_id', 'mpesa_receipt_number', 'status', 'created_at', 'updated_at')
    search_fields = ('user__username', 'phone_number', 'checkout_request_id', 'mpesa_receipt_number')
    list_filter = ('status', 'created_at')
