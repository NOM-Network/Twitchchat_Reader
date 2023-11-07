import requests

url = "https://streamlabs.com/api/v2.0/token"

headers = {"accept": "application/json"}

response = requests.post(url, headers=headers)

print(response.text)