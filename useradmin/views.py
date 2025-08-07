from django.shortcuts import render, redirect
from django.db.models import Sum, F, DecimalField, Case, When, Value
from django.db.models.functions import Cast, Coalesce
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from userauths.models import User
from core.models import CartOrder, CartOrderProducts, Product, Category, ProductReview, Image
from useradmin.forms import AddProductForm
from .constants import *
from django.contrib.auth.decorators import login_required, permission_required

import datetime

# Create your views here.
@login_required
def dashboard(request):
    revenue = CartOrder.objects.aggregate(price=Sum(AMOUNT))
    total_orders_count = CartOrder.objects.all()
    all_products = Product.objects.all()
    all_categories = Category.objects.all()
    new_customers = User.objects.all().order_by("-id")[:6]
    latest_orders = CartOrder.objects.select_related(
        'user', 
        'user__profile'
    ).annotate(
        display_id=F(DISPLAY_ID),
        full_name=F(FULL_NAME),
        email=F(EMAIL),
        phone=F(PHONE),
        total=Cast(
            Coalesce(F(AMOUNT), Value(0)), 
            output_field=DecimalField(max_digits=MAX_DIGITS_DECIMAL, decimal_places=DECIMAL_PLACES)
        )
    ).order_by('-order_date')[:10]
    
    this_month = datetime.datetime.now().month
    monthly_revenue = CartOrder.objects.filter(order_date__month=this_month).aggregate(price=Sum(AMOUNT))

    context = {
        "monthly_revenue": monthly_revenue,
        "revenue": revenue,
        "all_products": all_products,
        "all_categories": all_categories,
        "new_customers": new_customers,
        "latest_orders": latest_orders,
        "total_orders_count": total_orders_count,
    }
    return render(request, "useradmin/dashboard.html", context)

@login_required
def products(request):
    sort_by = request.GET.get('sort', 'title')
    order = request.GET.get('order', 'asc')

    if order == 'desc':
        sort_by = '-' + sort_by

    all_products = Product.objects.all().annotate(
        display_price=Cast(
            Coalesce('amount', Value(0)), 
            output_field=DecimalField(max_digits=MAX_DIGITS_DECIMAL, decimal_places=DECIMAL_PLACES)
        ),
        display_old_price=Cast(
            Coalesce('old_price', Value(0)), 
            output_field=DecimalField(max_digits=MAX_DIGITS_DECIMAL, decimal_places=DECIMAL_PLACES)
        ),
        discount_percent=Case(
            When(
                old_price__gt=0,
                then=Cast(
                    (Cast(Coalesce(F('old_price'), Value(0)), DecimalField(max_digits=MAX_DIGITS_DECIMAL, decimal_places=DECIMAL_PLACES)) - 
                     Cast(Coalesce(F('amount'), Value(0)), DecimalField(max_digits=MAX_DIGITS_DECIMAL, decimal_places=DECIMAL_PLACES))) * 100.0 / 
                    Cast(Coalesce(F('old_price'), Value(1)), DecimalField(max_digits=MAX_DIGITS_DECIMAL, decimal_places=DECIMAL_PLACES)),
                    output_field=DecimalField(max_digits=MAX_DIGITS_DECIMAL, decimal_places=DECIMAL_PLACES)
                )
            ),
            default=Value(0),
            output_field=DecimalField(max_digits=MAX_DIGITS_DECIMAL, decimal_places=DECIMAL_PLACES)
        )
    ).order_by(sort_by)

    all_categories = Category.objects.all()
    
    context = {
        "all_products": all_products,
        "all_categories": all_categories,
        'sort_by': request.GET.get('sort', 'title'),
        'order': request.GET.get('order', 'asc'),
    }
    return render(request, "useradmin/products.html", context)

@login_required
def add_product(request):
    if request.method == "POST":
        form = AddProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            
            if 'image' in request.FILES:
                Image.objects.create(
                    image=request.FILES['image'],
                    alt_text=product.title,
                    object_type='product',
                    object_id=product.pid,
                    is_primary=True
                )
            
            return redirect("useradmin:dashboard-products")
    else:
        form = AddProductForm()
    
    context = {
        'form': form
    }
    return render(request, "useradmin/add-products.html", context)
