from django.urls import path
from .views import UserRegistrationAPI, InventoryItemList, InventoryItemDetail
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('auth/register/', UserRegistrationAPI.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('items/', InventoryItemList.as_view(), name='item-list-create'),
    path('items/<int:pk>/', InventoryItemDetail.as_view(), name='item-detail'),
    
]