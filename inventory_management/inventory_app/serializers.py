from rest_framework.serializers import ModelSerializer
from .models import InventoryItem

class InventoryItemSerializer(ModelSerializer):
    class Meta:
        model = InventoryItem
        fields = '__all__'
