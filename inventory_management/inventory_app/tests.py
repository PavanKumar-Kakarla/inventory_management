from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

# Create your tests here.

class InventoryAPITest(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.refresh  = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)

        self.item_data = {'name': 'Test Item', 'description': 'Test Description', 'quantity': 10, 'price': 100.00}
        self.headers = {'HTTP_AUTHORIZATION': f'Bearer {self.access_token}'}

    def test_create_item_success(self):
        url = reverse('item-list-create')  # URL for creating an item
        response = self.client.post(url, self.item_data, format='json', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], self.item_data['name'])

    def test_create_item_unauthorized(self):
        url = reverse('item-list-create')
        response = self.client.post(url, self.item_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_item_list(self):
        url = reverse('item-list-create')
        response = self.client.get(url, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_item_not_found(self):
        url = reverse('item-detail', kwargs={'pk': 9999})  # Non-existent item
        response = self.client.get(url, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_item(self):
        # First, create the item
        create_url = reverse('item-list-create')
        response = self.client.post(create_url, self.item_data, format='json', **self.headers)
        item_id = response.data['id']
        
        # Then, update the item
        update_data = {'name': 'Updated Item', 'description': 'Updated Description', 'quantity': 8, 'price': 100.00}
        update_url = reverse('item-detail', kwargs={'pk': item_id})
        response = self.client.put(update_url, update_data, format='json', **self.headers)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], update_data['name'])

    def test_delete_item(self):
        # First, create the item
        create_url = reverse('item-list-create')
        response = self.client.post(create_url, self.item_data, format='json', **self.headers)
        item_id = response.data['id']
        
        # Then, delete the item
        delete_url = reverse('item-detail', kwargs={'pk': item_id})
        response = self.client.delete(delete_url, **self.headers)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)