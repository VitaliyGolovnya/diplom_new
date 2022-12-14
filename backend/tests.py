from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from backend.models import Order
from users.models import CustomUser

user_data = {'email': 'test@test.com',
                'password': 'test_password',
                'password2': 'test_password',
                'company': 'test_company',
                'position': 'test_position',
                'type': 'buyer',
                'name': 'test_name',
                'surname': 'test_surname',
                'middle_name': 'test_middle_name'}

user_url = reverse('signup')

class CustomUserTests(APITestCase):
    '''
    test user creation
    '''

    def test_signup_login(self):
        response = self.client.post(user_url, user_data, format='json')
        self.assertTrue(self.client.login(email='test@test.com', password='test_password'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(CustomUser.objects.get().email, 'test@test.com')


class OrderTest(APITestCase):

    def create_order(self):
        url = reverse('order-list')
        data = {
            'ordered_items': [],
        }
        self.client.post(user_url, user_data, format='json')
        self.client.login(email='test@test.com', password='test_password')
        response = self.client.post(url, data, format='json')
        return response

    def test_create_and_retrieve_order(self):
        '''
        test Order creation and retrieve
        '''
        response = self.create_order()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)

    def test_retrieve_orders_list(self):
        '''
        test Order list
        '''
        self.create_order()
        url = reverse('order-list')
        response = self.client.get(url, format='json')
        print(response.json())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]['ordered_items'], [])
