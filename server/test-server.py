import requests

url = "http://127.0.0.1:8000/image/"
files = {
    "file": open("test-images/high-contrast-cropped.png", "rb")
}  # Replace 'your_image.jpg'

params = {"n_concepts": 2, "n_products": 5}

response = requests.post(url, files=files, params=params)

if response.status_code == 200:
    print(response.json())
else:
    print("Error:", response.text)
