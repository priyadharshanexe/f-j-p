import unittest
import json

from app import app


class FlaskTestCase(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.client = app.test_client()

    # Home Page
    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    # Valid Product
    def test_product_exists(self):
        response = self.client.get('/product/p1')
        self.assertEqual(response.status_code, 200)

    # Invalid Product
    def test_product_not_found(self):
        response = self.client.get('/product/invalid')
        self.assertEqual(response.status_code, 404)

    # Empty Cart
    def test_get_cart(self):
        response = self.client.get('/api/cart')
        self.assertEqual(response.status_code, 200)

    # Add Item
    def test_add_to_cart(self):
        response = self.client.post(
            '/api/cart',
            data=json.dumps({
                "productId": "p1",
                "quantity": 1
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)

    # Wishlist
    def test_get_wishlist(self):
        response = self.client.get('/api/wishlist')
        self.assertEqual(response.status_code, 200)

    # Orders API
    def test_orders(self):
        response = self.client.get('/api/orders')
        self.assertEqual(response.status_code, 200)

    # Checkout Empty Cart
    def test_checkout_empty_cart(self):
        with self.client.session_transaction() as sess:
            sess['cart'] = []

        response = self.client.post(
            '/api/checkout',
            data=json.dumps({
                "shippingId": "standard"
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
