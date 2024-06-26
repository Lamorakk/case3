import logging
import aiohttp
import requests
from aiogram.handlers import message

from config import JWT_TOKEN

def post_new_user(data):
    url = 'http://localhost:6027/api/users/register'
    headers = {
        'Authorization': f'Bearer {JWT_TOKEN}',
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
    url = 'http://localhost:6027/api/users/reflink/{user_id}'
    try:
        headers = {
            'Authorization': f'Bearer {JWT_TOKEN}',
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
