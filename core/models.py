from django.db import models
from django.contrib.auth.models import User
from shortuuid.django_fields import ShortUUIDField

# Create your models here.

RATING = (
    (1,  "★☆☆☆☆"),
    (2,  "★★☆☆☆"),
    (3,  "★★★☆☆"),
    (4,  "★★★★☆"),
    (5,  "★★★★★"),
)

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
        
class Category(models.Model):
    cid = ShortUUIDField(unique=True, length=10, max_length=20,
                        prefix="cat", alphabet="abcdefgh12345")
    title = models.CharField(max_length=100, default="Food")
    image = models.ImageField(upload_to="category", default="category.jpg")

    class Meta:
        verbose_name_plural = "Categories"


class Product(models.Model):
    pid = ShortUUIDField(unique=True, length=10, max_length=20, alphabet="abcdefgh12345", primary_key=True)

    category = models.ForeignKey(
        'Category', on_delete=models.SET_NULL, null=True, related_name="products"
    )
    vendor = models.ForeignKey(
        'Vendor', on_delete=models.SET_NULL, null=True, related_name="products"
    )

    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)

    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    old_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    specifications = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=100, null=True, blank=True)
    stock_count = models.CharField(max_length=100, null=True, blank=True)
    life = models.CharField(max_length=100, null=True, blank=True)
    mfd = models.DateTimeField(null=True, blank=True)

    product_status = models.CharField(max_length=50, default="in_review")
    status = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    digital = models.BooleanField(default=False)

    sku = ShortUUIDField(unique=True, length=4, max_length=10, prefix="sku", alphabet="1234567890")

    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(null=True, blank=True)

    rating_avg = models.FloatField(default=0.0)

    class Meta:
        verbose_name_plural = "Products"

class ProductReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name="reviews")
    review = models.TextField()
    rating = models.IntegerField(choices=RATING, default=None)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Product Reviews"

from django.db import models
from django.contrib.auth.models import User

class ReturnRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='return_requests')
    order_product = models.ForeignKey('CartOrderProducts', on_delete=models.CASCADE, related_name='return_requests')
    reason = models.TextField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ReturnRequest #{self.pk} by {self.user.username}"

