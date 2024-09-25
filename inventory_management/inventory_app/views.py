from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions, status
from .models import InventoryItem
from .serializers import InventoryItemSerializer
from django.core.cache import cache
from django.contrib.auth.models import User
import logging

# Create your views here.

logger = logging.getLogger('inventory')

class UserRegistrationAPI(APIView):
    def post(self, request):
        logger.info(f'Received the new user request')
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')

        if not username or not password or not email:
            return Response({"error": "Username, password, and email are required"}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({"error": "User already exists."}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(username=username, password=password, email=email)
        user.save()
        logger.info(f'New user successfully registered')
        return Response({"message": "User created successfully."}, status=status.HTTP_201_CREATED)

class InventoryItemList(APIView):

    permission_classes = [permissions.IsAuthenticated]

    #List all items
    def get(self, request):
        logger.info(f'GET request received for inventory items')
        items = InventoryItem.objects.all()
        serializer = InventoryItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    #Adding new item
    def post(self, request):
        serializer = InventoryItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f'New item successfully added')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Received wrong data")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InventoryItemDetail(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        cache_key = f"item_{pk}"
        item = cache.get(cache_key)
        if not item:
            try:
                item = InventoryItem.objects.get(pk=pk)
                cache.set(cache_key, item, timeout=60*15)
            except InventoryItem.DoesNotExist:
                return None
        return item

    #Retriving single item by ID
    def get(self, request, pk):
        logger.info(f'GET request received for retriving {pk} item details')
        item = self.get_object(pk)
        if not item:
            logger.error(f"Item {pk} was not found")
            return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = InventoryItemSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    #Update the existing item
    def put(self, request, pk):
        item = self.get_object(pk)
        if not item:
            logger.error(f"Item {pk} was not found")
            return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = InventoryItemSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            cache.delete(f"item_{pk}")  #Clear the cache for this item after update
            logger.info(f'Item was successfully updated')
            return Response(serializer.data)
        logger.error(f"Received the wrong data")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    #Delete the item
    def delete(self, request, pk):
        item = self.get_object(pk)
        if not item:
            logger.error(f"Item {pk} was not found")
            return Response({"error": "Item not found"}, status=status.HTTP_404_NOT_FOUND)
        item.delete()
        cache.delete(f"item_{pk}")  #Clear the cache for this item after update
        logger.info(f'item was successfully deleted')
        return Response({"message": "Item deleted successfully"}, status=status.HTTP_204_NO_CONTENT)