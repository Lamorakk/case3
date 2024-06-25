import requests

def make_withdraw_request(api_url, tgid, token, data):

    try:
        response = requests.post(
            f"{api_url}/withdraws/{tgid}",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            json=data
        )

        response_data = response.json()
        print(response_data)
        return "https://google.com"
    except Exception as error:
        print(f"Error: {error}")
        raise  # Propagate the error so the calling code can handle it

# Example usage
api_url = "YOUR_API_URL"
tgid = "YOUR_TGID"
token = "YOUR_TOKEN"
data = {
    # Your data here
}

make_withdraw_request(api_url, tgid, token, data)
