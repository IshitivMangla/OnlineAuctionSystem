from django.urls import path
from . import views

urlpatterns = [
    # =========================
    # HTML ROUTES
    # =========================
    path('', views.home, name='home'),
    path('add/', views.add_item, name='add_item'),
    path('item/<int:id>/', views.item_detail, name='item_detail'),
    path('dashboard/', views.dashboard, name='dashboard'),  # ✅ Dashboard URL


    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('edit_item/<int:id>/', views.edit_item, name='edit_item'),

#     # =========================
#     # API ROUTES
#     # =========================
#     path('api/items/', views.api_items),
#     path('api/items/<int:id>/', views.api_item_detail),

#     # 🔥 FIXED NAME (important)
#     path('api/add_item/', views.add_item),
#     path('api/bid/<int:id>/', views.api_bid),
#     path('api/login/', views.api_login),
#     path('api/logout/', views.api_logout),
]