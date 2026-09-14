from django.db import models
from django.contrib.auth.models import User


class Item(models.Model):
    REPORT_TYPES = [
        ('LOST', 'Lost'),
        ('FOUND', 'Found'),
    ]

    CATEGORIES = [
        ('ID_CARD', 'ID Card'),
        ('WALLET', 'Wallet'),
        ('KEYS', 'Keys'),
        ('ELECTRONICS', 'Electronics'),
        ('BOOKS', 'Books'),
        ('OTHER', 'Other'),
    ]

    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('CLAIMED', 'Claimed'),
        ('CLOSED', 'Closed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    report_type = models.CharField(max_length=10, choices=REPORT_TYPES)
    item_name = models.CharField(max_length=150)
    category = models.CharField(max_length=30, choices=CATEGORIES)
    description = models.TextField()
    location = models.CharField(max_length=150)
    item_date = models.DateField()
    image = models.ImageField(
        upload_to='item_images/',
        blank=True,
        null=True
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='OPEN'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item_name} - {self.report_type}"

class ClaimRequest(models.Model):
    CLAIM_STATUS = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='claims'
    )

    claimant = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    message = models.TextField()

    status = models.CharField(
        max_length=10,
        choices=CLAIM_STATUS,
        default='PENDING'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["item", "claimant"],
                name="unique_claim_per_user_per_item"
            )
        ]

    def __str__(self):
        return f"Claim for {self.item.item_name}"   
