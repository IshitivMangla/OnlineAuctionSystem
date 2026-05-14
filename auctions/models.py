from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


# Default auction end time (1 day from now)
def default_end_time():
    return timezone.now() + timedelta(days=1)


class Item(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    starting_price = models.FloatField()

    # Optional image (safe)
    image = models.ImageField(upload_to='items/', blank=True, null=True)

    # IMPORTANT: must match views.py API
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="items"
    )

    # ✅ Seller can override, default still 24h
    end_time = models.DateTimeField(default=default_end_time)

    def __str__(self):
        return self.title

    # Get highest bid safely
    def highest_bid(self):
        return self.bids.order_by('-amount').first()

    # Extra helper (optional but useful)
    def is_ended(self):
        return timezone.now() > self.end_time

    # ✅ OPTIONAL (nice feature, no break)
    def time_left(self):
        return self.end_time - timezone.now()


class Bid(models.Model):
    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name='bids'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    amount = models.FloatField()
    bid_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-amount']  # highest bid first

    def __str__(self):
        return f"{self.user.username} - ₹{self.amount}"