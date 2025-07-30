from django.db import models
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe
from django.conf import settings
from taggit.managers import TaggableManager
from django_ckeditor_5.fields import CKEditor5Field
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

from django.contrib.auth.models import AbstractUser
from userauths.models import User
from .constants import ( RATING, RETURN_STATUS_CHOICES, PRODUCT_STATUS_CHOICES, OBJECT_TYPE_CHOICES, ORDER_STATUS_CHOICES, 
    MAX_LENGTH_MOBILE, MAX_LENGTH_ADDRESS,MAX_LENGTH_TEXT , MAX_LENGTH_TITLE, MAX_LENGTH_CONTACT,
    MAX_LENGTH_IMAGE_URL, MAX_LENGTH_OBJECT_TYPE, MAX_LENGTH_OBJECT_ID,
    MAX_LENGTH_IMAGE_TYPE, MAX_LENGTH_CODE,MAX_LENGTH_VID,SHIP_ON_TIME ,MIN,AUTHENTIC_RATING ,
    MAX_LENGTH_STOCK_COUNT, MAX_LENGTH_LIFE,MAX_LENGTH_ITEM,WARRANTY_PERIOD_TIME_MONTH ,DAY_RETURN ,
    MAX_LENGTH_PRODUCT_STATUS, MAX_LENGTH_ORDER_STATUS,MAX_DIGITS_AMOUNT,MAX_LENGTH_CID,MAX_LENGTH_PID,MAX_LENGTH_TYPE,MAX_LENGTH_SKU,MAX_LENGTH_RETRUNRQ_STATUS )

# Create your models here.
def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.id, filename)


#ok
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    mobile = models.CharField(max_length=MAX_LENGTH_MOBILE , null=True, blank=True)
    address = models.CharField(max_length=MAX_LENGTH_ADDRESS, null=True, blank=True)
    status = models.BooleanField(default=False)

    class Meta:
        db_table = 'address'
        verbose_name = "Address"
        verbose_name_plural = "Addresses"

    def __str__(self):
        return f"{self.user} - {self.address}"
  
#ok
class Image(models.Model):
    url = models.ImageField(upload_to='images/')
    alt_text = models.CharField(max_length=MAX_LENGTH_TEXT , null=True, blank=True)
    object_type = models.CharField(max_length=MAX_LENGTH_OBJECT_TYPE, choices=OBJECT_TYPE_CHOICES )  # e.g., 'Product', 'Category', 'Vendor'
    object_id = models.CharField(max_length=MAX_LENGTH_OBJECT_ID)    # e.g., pid, cid, vid
    is_primary = models.BooleanField(default=False)
    image_type = models.CharField(max_length=MAX_LENGTH_IMAGE_TYPE , null=True, blank=True)  # thumbnail, cover, etc.
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'image'
        verbose_name = "Image"
        verbose_name_plural = "Images"
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.object_type} - {self.object_id}"
#ok
class Vendor(models.Model):
    vid = models.CharField(max_length=MAX_LENGTH_VID, primary_key=True)
    title = models.CharField(max_length=MAX_LENGTH_TITLE)
    description = models.TextField()
    address = models.CharField(max_length=MAX_LENGTH_ADDRESS)
    contact = models.CharField(max_length=MAX_LENGTH_CONTACT)
    chat_resp_time = models.PositiveIntegerField(help_text="Thời gian phản hồi (phút)")
    shipping_on_time = models.PositiveIntegerField(
        help_text="Tỷ lệ giao hàng đúng hẹn (%)",
        validators=[MinValueValidator(MIN), MaxValueValidator(SHIP_ON_TIME )]
    )
    
    authentic_rating = models.FloatField(
        help_text="Điểm đánh giá độ tin cậy, 0.0-5.0",
        validators=[MinValueValidator(MIN), MaxValueValidator(AUTHENTIC_RATING)]
    )
    
    days_return = models.PositiveIntegerField(
        help_text="Số ngày cho phép hoàn trả",
        validators=[MinValueValidator(MIN), MaxValueValidator(DAY_RETURN)]  # giới hạn trong 2 tháng
    )

    warranty_period = models.PositiveIntegerField(
        help_text="Thời gian bảo hành (tháng)",
        validators=[MinValueValidator(MIN), MaxValueValidator(WARRANTY_PERIOD_TIME_MONTH )]  # tối đa 5 năm
    )
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} (ID: {self.vid})"
    class Meta:
        db_table = 'vendor'
        verbose_name = "Vendor"
        verbose_name_plural = "Vendors"

#ok
class Coupon(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    code = models.CharField(max_length=MAX_LENGTH_CODE , unique=True)
    discount = models.FloatField()
    active = models.BooleanField(default=True)
    expiry_date = models.DateTimeField()
    min_order_amount = models.DecimalField(max_digits=MAX_DIGITS_AMOUNT, decimal_places=2)
    max_discount_amount = models.DecimalField(max_digits=MAX_DIGITS_AMOUNT, decimal_places=2)
    apply_once_per_user = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} - {self.vendor.title}"
   
    class Meta:
        db_table = 'coupon'
        verbose_name = "Coupon"
        verbose_name_plural = "Coupons"

#ok
class CouponUser(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"{self.user} - {self.coupon.code}"
    class Meta:
        db_table = 'coupon_user'
        constraints = [
            models.UniqueConstraint(fields=['coupon', 'user'], name='unique_coupon_user')
        ]

#ok       
class Category(models.Model):
    cid = models.CharField(max_length=MAX_LENGTH_CID, primary_key=True)
    title = models.CharField(max_length=MAX_LENGTH_TITLE)

    # Self-referencing ForeignKey
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children'
    )

    def __str__(self):
        if self.parent:
            return f"{self.parent.title} ➝ {self.title}"
        return self.title

    class Meta:
        db_table = 'category'
        verbose_name = "Category"
        verbose_name_plural = "Categories"
#ok

class Product(models.Model):
    pid = ShortUUIDField(unique=True, length=10, max_length=MAX_LENGTH_PID , alphabet="abcdefgh12345", primary_key=True)

    category = models.ForeignKey(
        'Category', on_delete=models.SET_NULL, null=True, related_name="products"
    )
    vendor = models.ForeignKey(
        'Vendor', on_delete=models.SET_NULL, null=True, related_name="products"
    )
    title = models.CharField(max_length=MAX_LENGTH_TITLE)
    description = models.TextField(null=True, blank=True)
    amount = models.DecimalField(max_digits=MAX_DIGITS_AMOUNT, decimal_places=2, default=0.00)
    old_price = models.DecimalField(max_digits=MAX_DIGITS_AMOUNT, decimal_places=2, default=0.00)
    specifications = models.TextField(null=True, blank=True)
    type = models.CharField(max_length=MAX_LENGTH_TYPE, null=True, blank=True)
    stock_count = models.CharField(max_length=MAX_LENGTH_STOCK_COUNT , null=True, blank=True)
    life = models.CharField(max_length=MAX_LENGTH_LIFE, null=True, blank=True)
    mfd = models.DateTimeField(null=True, blank=True)
    product_status = models.CharField(
        max_length=MAX_LENGTH_PRODUCT_STATUS,
        choices=PRODUCT_STATUS_CHOICES,
        default='in_review'
        )
    status = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    featured = models.BooleanField(default=False)
    digital = models.BooleanField(default=False)
    sku = ShortUUIDField(unique=True, length=4, max_length=MAX_LENGTH_SKU, prefix="sku", alphabet="1234567890")
    date = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    rating_avg = models.FloatField(default=0.0)

    class Meta:
        db_table = 'product'
        verbose_name = "Product"
        verbose_name_plural = "Products"
        ordering = ['-date']

    def __repr__(self):
        return f"<Product {self.title}>"
#ok
class ProductReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name="reviews")
    review = models.TextField()
    rating = models.IntegerField(choices=RATING, default=None)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "product_review"
        verbose_name = "Product Review"
        verbose_name_plural = "Product Reviews"
        ordering = ['-date']

    def __str__(self):
        return f"{self.user} - {self.product} ({self.rating}★)"


#ok
class ReturnRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='return_requests')
    order_product = models.ForeignKey('CartOrderProducts', on_delete=models.CASCADE, related_name='return_requests')
    reason = models.TextField()
    status = models.CharField(max_length=MAX_LENGTH_RETRUNRQ_STATUS, choices=RETURN_STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        username = self.user.username if self.user else "Unknown User"
        return f"ReturnRequest #{self.pk} - {username}"

    class Meta:
        db_table = 'return_request'
        verbose_name = "Return Request"
        verbose_name_plural = "Return Requests"
        ordering = ['-created_at']
#ok
class CartOrder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cart_orders")
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="cart_orders")
    amount = models.DecimalField(max_digits=MAX_DIGITS_AMOUNT, decimal_places=2)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True, related_name="cart_orders")
    paid_status = models.BooleanField(default=False)
    order_status = models.CharField(
        max_length=MAX_LENGTH_ORDER_STATUS,
        choices=ORDER_STATUS_CHOICES,
        default='processing'
    )
    order_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.pk} - {self.user.username}"

    class Meta:
        db_table = 'cart_order'
        verbose_name = "Cart Order"
        verbose_name_plural = "Cart Orders"
        ordering = ['-order_date']

#ok
class CartOrderProducts(models.Model):
    order = models.ForeignKey(CartOrder, on_delete=models.CASCADE, related_name='order_products')
    item = models.CharField(max_length=MAX_LENGTH_ITEM)
    image = models.CharField(max_length=MAX_LENGTH_IMAGE_URL)
    qty = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=MAX_DIGITS_AMOUNT, decimal_places=2)
    total = models.DecimalField(max_digits=MAX_DIGITS_AMOUNT, decimal_places=2)

    def __str__(self):
        return f"{self.item} (x{self.qty})"

    class Meta:
        db_table = 'cart_order_products'
        verbose_name = "Cart Order Product"
        verbose_name_plural = "Cart Order Products"
        ordering = ['-id']