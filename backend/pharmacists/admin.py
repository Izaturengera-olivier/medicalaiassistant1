"""Admin registrations for pharmacists. Populated in later phases."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import PharmacistReview


@admin.register(PharmacistReview)
class PharmacistReviewAdmin(admin.ModelAdmin):
    """Admin interface for PharmacistReview."""

    list_display = ["prescription", "pharmacist", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["prescription__id", "pharmacist__email"]
    readonly_fields = ["created_at", "updated_at"]
