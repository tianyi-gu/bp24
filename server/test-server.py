import requests

url = "http://127.0.0.1:8000/image/"
files = {"file": open("test-images/high-contrast-cropped.png", "rb")}  # Replace 'your_image.jpg'

response = requests.post(url, files=files)

if response.status_code == 200:
    print(response.json())
else:
    print("Error:", response.text)
