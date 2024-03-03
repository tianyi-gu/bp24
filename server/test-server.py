import requests

# url = "https://vr1db662i7.execute-api.us-east-1.amazonaws.com/init/image"
url = "http://localhost:8000/image"
files = {
    "file": open("test-images/high-contrast-cropped.png", "rb")
}  # Replace 'your_image.jpg'

data = {"n_concepts": 2, "n_products": 5}

response = requests.post(url, files=files, data=data)

if response.status_code == 200:
    print(response.json())
else:
    print("Error:", response.text)
