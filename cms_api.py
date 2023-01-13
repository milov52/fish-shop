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

def add_to_cart(cart_id, product_id, quantity):
    access_token = get_access_token()
    headers = {
        'Authorization': f'Bearer {access_token.json().get("access_token")}'}

    cart_data = {
        "data": {
            "id": product_id,
            "type": "cart_item",
            "quantity": quantity
        }
    }
    cart = requests.post(f'https://api.moltin.com/v2/carts/{cart_id}/items', json=cart_data, headers=headers)


def get_cart(cart_id):
    access_token = get_access_token()
    headers = {
        'Authorization': f'Bearer {access_token.json().get("access_token")}'}
    cart = requests.get(f'https://api.moltin.com/v2/carts/{cart_id}', headers=headers)
    cart_items = requests.get(f'https://api.moltin.com/v2/carts/{cart_id}/items', headers=headers)


    print(cart.json())
    print(cart_items.json())

def get_products(product_id=0):
    access_token = get_access_token()
    headers = {
        'Authorization': f'Bearer {access_token.json().get("access_token")}'}

    pcm_url = os.environ.get("BASE_URL")
    if product_id:
        product = {}

        product_data = requests.get(f'{pcm_url}/products/{product_id}', headers=headers)
        product_data = product_data.json()["data"]

        file_id = product_data["relationships"]["main_image"]["data"]["id"]
        image_data = get_file_by_id(file_id)

        product["file_id"] = file_id
        product["image_path"] = image_data["data"]["link"]["href"]
        product["name"] = product_data["name"]
        product["description"] = product_data["description"]
        product["price"] = product_data["meta"]["display_price"]["with_tax"]["formatted"]
        product["stock"] = product_data["meta"]["stock"]["level"]

        return product
    else:
        products_data = requests.get(f'{pcm_url}/products/', headers=headers)
        products_data = products_data.json()
        products = [{product["id"], product["name"]} for product in products_data["data"]]
        return products

def get_file_by_id(file_id):
    access_token = get_access_token()
    headers = {
        'Authorization': f'Bearer {access_token.json().get("access_token")}'}

    file_data = requests.get(f'https://api.moltin.com/v2/files/{file_id}', headers=headers)
    return file_data.json()


def main():
    load_dotenv()
    # chat_id = 130324158
    product_id = "31ca00db-fd4a-480f-ad92-4dc69f6f839b"
    # count = 2
    # # add_to_cart(chat_id, product_id, count)
    # get_cart(chat_id)
    print(get_products(product_id))

if __name__ == '__main__':
    main()