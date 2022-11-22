from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.test import Client
from backend.models import Order
from backend.serializers import CustomUserSerializer
from users.models import CustomUser


class CustomUserTests(APITestCase):
    '''
    test user creation
    '''

    def test_signup(self):
        c = Client()
        url = reverse('signup')
        data = {'email': 'test@test.com',
                'password': 'test_password',
                'password2': 'test_password',
                'company': 'test_company',
                'position': 'test_position',
                'type': 'buyer',
                'name': 'test_name',
                'surname': 'test_surname',
                'middle_name': 'test_middle_name'}
        response = c.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(CustomUser.objects.get().email, 'test@test.com')


class OrderTest(APITestCase):
    def create_order(self):
        c = Client()
        url = reverse('order-list')
        data = {
            'ordered_items': [],
        }
        CustomUser.objects.create_user(
            email='test@test.com', password='test_password'
        )
        logged_in = c.login(username='test@test.com', password='test_password')
        print(logged_in)
        response = c.post(url, data, format='json')
        return response

    def test_create_and_retrieve_order(self):
        '''
        test Order creation and retrieve
        '''
        response = self.create_order()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
