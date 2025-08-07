from django.urls import path
from useradmin import views

app_name = "useradmin"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("products/", views.products, name="dashboard-products"),
    path("add-products/", views.add_product, name="dashboard-add-products"),
]
