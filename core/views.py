from django.shortcuts import render
from django.http import HttpResponse
from .fake_data import *
from core.models import *

# Create your views here.
def index (request):
    return render(request, 'core/index.html')

def product_list_view(request):
    return render(request, 'core/product-list.html')

def about_us(request):
    return render(request, "core/about_us.html")

def customer_dashboard(request):
    return render(request, 'core/dashboard.html')

def search_view(request):
    return render(request, "core/search.html")

def checkout(request):
    context = {}
    return render(request, "core/checkout.html", context)

def payment_completed_view(request):
    context = {
        "order": get_sample_order(),
    }
    return render(request, 'core/payment-completed.html', context)

def payment_failed_view(request):
    return render(request, 'core/payment-failed.html')

def order_detail(request, id):
    context = {"order_items": get_order_items()}
    return render(request, 'core/order-detail.html', context)

def category_list_view(request):
    context = {"categories": get_categories()}
    return render(request, 'core/category-list.html', context)

def category_product_list__view(request, cid):
    products = get_products_by_category(cid)
    
    # Add reviews count to each product
    for product in products:
        product['reviews_count'] = product['reviews']['all']['count']
    
    context = {
        "category": get_category_by_id(cid),
        "products": products,
    }
    return render(request, "core/category-product-list.html", context)

def vendor_list_view(request):
    vendors = Vendor.objects.all()
    
    # Debug: Print vendor info
    for vendor in vendors:
        print(f"Vendor: {vendor.title}")
        print(f"  - primary_image_url: {vendor.primary_image_url}")
        print(f"  - image_set count: {vendor.image_set.count()}")
        for img in vendor.image_set.all():
            print(f"    - Image: {img.url.url}, is_primary: {img.is_primary}, object_type: {img.object_type}")
    
    context = {
        "vendors": vendors,
    }
    return render(request, "core/vendor-list.html", context)

def vendor_detail_view(request, vid):
    vendor = Vendor.objects.get(vid=vid)
    products = Product.objects.filter(vendor=vendor, product_status="published").order_by("-date")
    categories = Category.objects.all()

    context = {
        "vendor": vendor,
        "products": products,
        "categories": categories,
    }
    return render(request, "core/vendor-detail.html", context)
