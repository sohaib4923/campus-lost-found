from django.contrib import admin
from .models import Item, ClaimRequest


@admin.action(description="Approve selected claims")
def approve_claims(modeladmin, request, queryset):
    for claim in queryset:
        if claim.status == "PENDING":
            claim.status = "APPROVED"
            claim.save()

            claim.item.status = "CLAIMED"
            claim.item.save()


@admin.action(description="Reject selected claims")
def reject_claims(modeladmin, request, queryset):
    queryset.filter(status="PENDING").update(status="REJECTED")


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = (
        "item_name",
        "report_type",
        "category",
        "location",
        "status",
        "user",
        "created_at",
    )

    list_filter = (
        "report_type",
        "category",
        "status",
    )

    search_fields = (
        "item_name",
        "location",
        "description",
    )


@admin.register(ClaimRequest)
class ClaimRequestAdmin(admin.ModelAdmin):
    list_display = (
        "item",
        "claimant",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
    )

    search_fields = (
        "item__item_name",
        "claimant__username",
        "message",
    )

    actions = [
        approve_claims,
        reject_claims,
    ]