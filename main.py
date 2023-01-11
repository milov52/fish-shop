import os

import requests
from dotenv import load_dotenv




def main():
    load_dotenv()

    data = {
        'client_id': os.environ.get("CLIENT_ID"),
        'client_secret': os.environ.get("CLIENT_SECRET"),
        'grant_type': os.environ.get("GRANT_TYPE"),
    }

    pcm_url = os.environ.get("PCM_URL")

    access_token = requests.post(f'https://api.moltin.com/oauth/access_token', data=data)
    headers = {
        'Authorization': f'Bearer {access_token.json().get("access_token")}',
    }
    products = requests.get(f'{pcm_url}/products', headers=headers)
    product_id = products.json().get("data")[0].get("id")
    print(product_id)


if __name__ == '__main__':
    main()