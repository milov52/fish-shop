import os
from datetime import datetime

import requests


def get_access_token(client_id: str):
    data = {
        'client_id': client_id,
        'client_secret': os.environ.get("CLIENT_SECRET"),
        'grant_type': os.environ.get("GRANT_TYPE"),
    }
    response_access_token = requests.post(
        'https://api.moltin.com/oauth/access_token', data=data
    )
    response_access_token.raise_for_status()

    access_token = response_access_token.json()
    os.environ.setdefault('MOLTIN_TOKEN_EXPIRES_TIME', str(access_token['expires']))
    os.environ.setdefault('ACCESS_TOKEN', access_token['access_token'])


def check_access_token(client_id: str):
    token_expires_time = os.getenv('MOLTIN_TOKEN_EXPIRES_TIME')
    timestamp = int(datetime.now().timestamp())
    if not token_expires_time or int(token_expires_time) < timestamp:
        get_access_token(client_id)


def add_to_cart(cart_id: str, product_id: str, quantity: int, client_id: str):
    check_access_token(client_id)
    access_token = os.getenv('ACCESS_TOKEN')
    headers = {
        'Authorization': f'Bearer {access_token}'}

    cart_data = {
        "data": {
            "id": product_id,
            "type": "cart_item",
            "quantity": quantity
        }
    }
    cart = requests.post(f'https://api.moltin.com/v2/carts/{cart_id}/items',
                         json=cart_data,
                         headers=headers)
    cart.raise_for_status()


def get_cart(cart_id: str, client_id: str):
    check_access_token(client_id)
    access_token = os.getenv('ACCESS_TOKEN')

    headers = {
        'Authorization': f'Bearer {access_token}'}
    cart_responce = requests.get(f'https://api.moltin.com/v2/carts/{cart_id}',
                                 headers=headers)
    cart_responce.raise_for_status()
    cart_items_response = requests.get(f'https://api.moltin.com/v2/carts/{cart_id}/items',
                                       headers=headers)
    cart_items_response.raise_for_status()

    cart = []
    for cart_items in cart_items_response.json()["data"]:
        cart_item = {}
        cart_item["id"] = cart_items["id"]
        cart_item["name"] = cart_items["name"]
        cart_item["description"] = cart_items["description"]
        cart_item["price"] = cart_items["unit_price"]["amount"]
        cart_item["quantity"] = cart_items["quantity"]
        cart_item["amount"] = cart_items["value"]["amount"]
        cart.append(cart_item)

    full_amount = cart_responce.json()["data"]["meta"]["display_price"]["with_tax"]["amount"]
    return {"cart_items": cart, "full_amount": full_amount}


def delete_from_cart(cart_id: str, product_id: str, client_id: str):
    check_access_token(client_id)
    access_token = os.getenv('ACCESS_TOKEN')
    headers = {
        'Authorization': f'Bearer {access_token}'}

    cart = requests.delete(f'https://api.moltin.com/v2/carts/{cart_id}/items/{product_id}',
                           headers=headers)
    cart.raise_for_status()


def get_products(client_id, product_id=0):
    check_access_token(client_id)
    access_token = os.getenv('ACCESS_TOKEN')
    headers = {
        'Authorization': f'Bearer {access_token}'}

    pcm_url = os.environ.get("BASE_URL")
    if product_id:
        product = {}

        product_data = requests.get(f'{pcm_url}/products/{product_id}',
                                    headers=headers)
        product_data.raise_for_status()
        product_data = product_data.json()["data"]

        file_id = product_data["relationships"]["main_image"]["data"]["id"]
        image_data = get_file_by_id(file_id, client_id)

        product["file_id"] = file_id
        product["image_path"] = image_data["data"]["link"]["href"]
        product["name"] = product_data["name"]
        product["description"] = product_data["description"]
        product["price"] = product_data["meta"]["display_price"]["with_tax"]["formatted"]
        product["stock"] = product_data["meta"]["stock"]["level"]

        return product
    else:
        products_data = requests.get(f'{pcm_url}/products/',
                                     headers=headers)
        products_data.raise_for_status()

        products_data = products_data.json()
        products = [{"id": product["id"], "name": product["name"]} for product in products_data["data"]]
        return products


def get_file_by_id(file_id: str, client_id: str):
    check_access_token(client_id)
    access_token = os.getenv('ACCESS_TOKEN')
    headers = {
        'Authorization': f'Bearer {access_token}'}

    file_data = requests.get(f'https://api.moltin.com/v2/files/{file_id}',
                             headers=headers)
    file_data.raise_for_status()
    return file_data.json()


def create_user_account(name: str, email: str, client_id: str):
    check_access_token(client_id)
    access_token = os.getenv('ACCESS_TOKEN')
    headers = {
        'Authorization': f'Bearer {access_token}'}

    json_data = {
        'data': {
            'type': 'customer',
            'name': name,
            'email': email,
        },
    }

    response_create_customer = requests.post(
        'https://api.moltin.com/v2/customers',
        headers=headers,
        json=json_data
    )
    response_create_customer.raise_for_status()
