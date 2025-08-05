from django.shortcuts import render
from django.http import HttpResponse
from django.contrib import messages
from django.shortcuts import redirect
from django.http import JsonResponse
from .models import Product
from django.template.loader import render_to_string
from django.db.models import Avg
from core.models import ProductReview
from django.shortcuts import get_object_or_404
from core.models import Image
from core.models import Vendor
from django.core.paginator import Paginator
from django.db.models import Q
from core.models import Category

# Create your views here.
def index (request):
    return render(request, 'core/index.html')

def cart_view(request):
    cart_total_amount = 0
    if 'cart_data_obj' in request.session:
        for p_id, item in request.session['cart_data_obj'].items():
            cart_total_amount += int(item['qty']) * float(item['price'])
        return render(request, "core/cart.html", {
            "cart_data": request.session['cart_data_obj'],
            'totalcartitems': len(request.session['cart_data_obj']),
            'cart_total_amount': cart_total_amount
        })
    else:
        messages.warning(request, "Your cart is empty")
        return redirect("core:index")
def add_to_cart(request):
    product_id = request.GET.get('id')
    qty = int(request.GET.get('qty', 1))

    if qty <= 0:
        return JsonResponse({'error': 'Quantity must be greater than 0'}, status=400)

    product = get_object_or_404(Product, pid=product_id)
    image_obj = Image.objects.filter(object_type='Product', object_id=product_id, is_primary=True).first()

    cart_product = {
        product_id: {
            'title': product.title,
            'qty': qty,
            'price': float(product.amount),
            'image': image_obj.url if image_obj else '',
            'pid': product.pid,
        }
    }

    cart_data = request.session.get('cart_data_obj', {})

    if product_id in cart_data:
        cart_data[product_id]['qty'] += qty
    else:
        cart_data.update(cart_product)

    request.session['cart_data_obj'] = cart_data

    return JsonResponse({
        "data": cart_data,
        "totalcartitems": len(cart_data)
    })
def delete_item_from_cart(request):
    product_id = str(request.GET.get('id'))

    cart_data = request.session.get('cart_data_obj', {})

    if product_id in cart_data:
        del cart_data[product_id]
        request.session['cart_data_obj'] = cart_data

    cart_total_amount = sum(
        int(item['qty']) * float(item['price'])
        for item in cart_data.values()
    )

    context_html = render_to_string("core/async/cart-list.html", {
        "cart_data": cart_data,
        "totalcartitems": len(cart_data),
        "cart_total_amount": cart_total_amount
    })
    return HttpResponse(context_html)

from django.template.loader import render_to_string
from django.http import HttpResponse

def update_cart(request):
    product_id = str(request.GET.get('id'))
    product_qty = request.GET.get('qty')

    cart_data = request.session.get('cart_data_obj', {})

    if product_id in cart_data:
        cart_data[product_id]['qty'] = int(product_qty)
        request.session['cart_data_obj'] = cart_data

    cart_total_amount = sum(int(item['qty']) * float(item['price']) for item in cart_data.values())

    context_html = render_to_string("core/async/cart-list.html", {
        "cart_data": cart_data,
        "totalcartitems": len(cart_data),
        "cart_total_amount": cart_total_amount
    })

    return HttpResponse(context_html)

def ajax_add_review(request, pid):
    product = Product.objects.get(pk=pid)
    user = request.user

    review = ProductReview.objects.create(
        user=user,
        product=product,
        review = request.POST['review'],
        rating = request.POST['rating'],
    )

    context = {
        'user': user.username,
        'review': request.POST['review'],
        'rating': request.POST['rating'],
    }

    average_reviews = ProductReview.objects.filter(product=product).aggregate(rating=Avg("rating"))

    return JsonResponse(
       {
         'bool': True,
        'context': context,
        'average_reviews': average_reviews
       }
    )
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
def search_view(request):
    return render(request, "core/search.html")

def product_detail_view(request, pid):
    return render(request, "core/product-detail.html")

def vendor_list_view(request):
    # Get search parameter
    search_query = request.GET.get('search', '')
    
    # Get sort parameter from request with validation
    sort_by = request.GET.get('sort', 'title')
    order = request.GET.get('order', 'asc')
    
    # Validate sort_by parameter
    valid_sort_fields = ['title', 'date', 'authentic_rating', 'shipping_on_time', 'chat_resp_time']
    if sort_by not in valid_sort_fields:
        sort_by = 'title'
    
    # Validate order parameter
    if order not in ['asc', 'desc']:
        order = 'asc'
    
    # Get page parameter
    page_number = request.GET.get('page', 1)
    
    vendors = Vendor.objects.all()
    
    # Apply search filter
    if search_query:
        vendors = vendors.filter(
            Q(title__icontains=search_query) |
            Q(vid__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(address__icontains=search_query)
        )
    
    # Apply sorting with improved logic
    sort_mapping = {
        'title': 'title',
        'date': 'date',
        'authentic_rating': 'authentic_rating',
        'shipping_on_time': 'shipping_on_time',
        'chat_resp_time': 'chat_resp_time'
    }
    
    sort_field = sort_mapping.get(sort_by, 'title')
    if order == 'desc':
        sort_field = f'-{sort_field}'
    
    vendors = vendors.order_by(sort_field)
    
    # Apply pagination
    paginator = Paginator(vendors, 12)  # Show 12 vendors per page
    page_obj = paginator.get_page(page_number)
    

    
    context = {
        "vendors": page_obj,
        "sort_by": sort_by,
        "order": order,
        "search_query": search_query,
        "page_obj": page_obj,
        "get_sorting_url": get_sorting_url,
        "base_params": {"search": search_query} if search_query else {},
    }
    return render(request, "core/vendor-list.html", context)

def vendor_detail_view(request, vid):
    vendor = Vendor.objects.get(vid=vid)
    
    # Get sort parameters for products with validation
    sort_by = request.GET.get('sort', 'date')
    order = request.GET.get('order', 'desc')
    
    # Validate sort_by parameter
    valid_sort_fields = ['date', 'title', 'price', 'rating']
    if sort_by not in valid_sort_fields:
        sort_by = 'date'
    
    # Validate order parameter
    if order not in ['asc', 'desc']:
        order = 'desc'
    
    products = Product.objects.filter(vendor=vendor, product_status="published")
    
    # Apply sorting to products with improved logic
    sort_mapping = {
        'date': 'date',
        'title': 'title',
        'price': 'amount',
        'rating': 'rating_avg'
    }
    
    sort_field = sort_mapping.get(sort_by, 'date')
    if order == 'desc':
        sort_field = f'-{sort_field}'
    
    products = products.order_by(sort_field)
    
    categories = Category.objects.all()

    context = {
        "vendor": vendor,
        "products": products,
        "categories": categories,
        "sort_by": sort_by,
        "order": order,
        "get_sorting_url": get_sorting_url,
        "base_params": {},
    }
    return render(request, "core/vendor-detail.html", context)

def get_sorting_url(request, sort_by, order):
    params = request.GET.copy()
    params['sort'] = sort_by
    params['order'] = order
    return f"{request.path}?{params.urlencode()}"
