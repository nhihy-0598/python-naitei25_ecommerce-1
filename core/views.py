from django.shortcuts import render
from django.http import HttpResponse

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

def product_detail_view (request):
    return render(request, "core/product-detail.html")