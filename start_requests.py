import logging
import aiohttp
import requests
from aiogram.handlers import message

from config import JWT_TOKEN

Url = 'http://localhost:6027/api/users/register'
token = 'eyJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJzZWxmIiwic3ViIjoidXNlcjEyMyIsImV4cCI6MTcxOTUyNDQ3NiwiaWF0IjoxNzE5MTY0NDc2LCJzY29wZSI6IkFETUlOIn0.2_sKML_7gl0g5UxUgSb8u_PtflcKqm0pnrL9O7y3Ms3gx71-2k4U1jkGsGkc6UP1lKj9yi9gDIvBr7qfcipmBg'

def post_new_user(data):
    url = 'http://localhost:6027/api/users/register'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code in {200, 201}:
        return response.json()
    else:
        logging.error(f"Failed to submit data: {response.status_code}")
        logging.error(response.text)
        return None


def get_user_ref(user_id):
    url = f'http://localhost:6027/api/users/reflink/{user_id}'
    try:
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        response = requests.get(url, headers=headers, json=user_id)

        if response.status_code == 200:
            return response.text
        else:
            logging.error(f"Failed to get referral link: {response.status_code}")
            return None

    except Exception as e:
        logging.error(f"Exception occurred: {e}")
        return None



# # Example usage
# api_url = "YOUR_API_URL"
# tgid = "YOUR_TGID"
# token = "YOUR_TOKEN"
# data = {
#     # Your data here
# }

# make_withdraw_request(api_url, tgid, token, data)

# def make_withdraw_request(api_url, tgid, token, data):
#
#     try:
#         response = requests.post(
#             f"{api_url}/withdraws/{tgid}",
#             headers={
#                 "Authorization": f"Bearer {token}",
#                 "Content-Type": "application/json"
#             },
#             json=data
#         )
#
#         response_data = response.json()
#         print(response_data)
#         return "https://google.com"
#     except Exception as error:
#         print(f"Error: {error}")
#         raise  # Propagate the error so the calling code can handle it
#
