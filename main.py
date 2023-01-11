import getopt
import json
import os

import requests
from dotenv import load_dotenv


def add_to_cart(product_id):
    cart_data = {
        "data": {
            "id": product_id,
            "type": "cart_item",
            "quantity": 1
        }
    }
    cart = requests.post('https://api.moltin.com/v2/carts/1/items/', json=cart_data, headers=headers)
    print(cart.json())


def main():
    load_dotenv()

    data = {
        'client_id': os.environ.get("CLIENT_ID"),
        'client_secret': os.environ.get("CLIENT_SECRET"),
        'grant_type': os.environ.get("GRANT_TYPE"),
    }

    pcm_url = os.environ.get("BASE_URL")

    access_token = requests.post('https://api.moltin.com/oauth/access_token', data=data)
    headers = {
        'Authorization': f'Bearer {access_token.json().get("access_token")}',
    }

    products = requests.get(f'{pcm_url}/products', headers=headers)
    print(products.json())
    product_id = products.json().get("data")[0].get("id")
    print(product_id)

    add_to_cart(product_id)


    token = os.environ.get("TG_TOKEN")


if __name__ == '__main__':
    main()