import requests

api_url = "https://x922hzaqgh.execute-api.eu-west-1.amazonaws.com/items"
response = requests.get(api_url)
print(response.json())