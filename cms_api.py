import getopt
import json
import os

import requests
from dotenv import load_dotenv

def get_access_token():
    data = {
        'client_id': os.environ.get("CLIENT_ID"),
        'client_secret': os.environ.get("CLIENT_SECRET"),
        'grant_type': os.environ.get("GRANT_TYPE"),
    }
    access_token = requests.post('https://api.moltin.com/oauth/access_token', data=data)
    return access_token

def add_to_cart(product_id):
    cart_data = {
        "data": {
            "id": product_id,
            "type": "cart_item",
            "quantity": 1
        }
    }
    cart = requests.post('https://api.moltin.com/v2/carts/1/items/', json=cart_data, headers=headers)

def get_products(product_id=0):
    access_token = get_access_token()

    headers = {
        'Authorization': f'Bearer {access_token.json().get("access_token")}'}

    pcm_url = os.environ.get("BASE_URL")
    if product_id:
        products = requests.get(f'{pcm_url}/products/{product_id}', headers=headers)
    else:
        products = requests.get(f'{pcm_url}/products/', headers=headers)

    products = products.json().get("data")
    return products

def get_file_by_id(file_id):
    access_token = get_access_token()
    headers = {
        'Authorization': f'Bearer {access_token.json().get("access_token")}'}
    file_data = requests.get(f'https://api.moltin.com/v2/files/{file_id}', headers=headers)
    return file_data.json()


def main():
    load_dotenv()
    product_id = "88dcac90-2829-4970-afc9-beddd29dbc7f"
    get_file_by_id(product_id)


if __name__ == '__main__':
    main()