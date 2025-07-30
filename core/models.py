from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Vendor(models.Model):
    vid = models.CharField(max_length=100, primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    address = models.CharField(max_length=500)
    contact = models.CharField(max_length=100)
    chat_resp_time = models.CharField(max_length=50)
    shipping_on_time = models.CharField(max_length=50)
    authentic_rating = models.CharField(max_length=50)
    days_return = models.CharField(max_length=50)
    warranty_period = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'vendor'

class Coupon(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    code = models.CharField(max_length=50, unique=True)
    discount = models.FloatField()
    active = models.BooleanField(default=True)
    expiry_date = models.DateTimeField()
    min_order_amount = models.DecimalField(max_digits=10, decimal_places=2)
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    apply_once_per_user = models.BooleanField(default=True)

    def __str__(self):
        return self.code

    class Meta:
        db_table = 'coupon'

class CouponUser(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'coupon_user'
        unique_together = ('coupon', 'user')
