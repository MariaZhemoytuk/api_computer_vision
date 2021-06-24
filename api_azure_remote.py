import json
import os
import sys
import requests
import time
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()
missing_env = False
if 'COMPUTER_VISION_ENDPOINT' in os.environ:
    endpoint = os.getenv('COMPUTER_VISION_ENDPOINT')
else:
    print("From Azure Cognitive Service, retrieve your endpoint.")
    missing_env = True

if 'COMPUTER_VISION_SUBSCRIPTION_KEY' in os.environ:
    subscription_key = os.getenv('COMPUTER_VISION_SUBSCRIPTION_KEY')
else:
    print("From Azure Cognitive Service, retrieve your subscription key.")
    missing_env = True

if missing_env:
    print("**Restart your shell or IDE for changes to take effect.**")
    sys.exit()

text_recognition_url = endpoint + "/vision/v3.2/read/analyze"

image_url = "https://www.in.gov/isp/labs/images/check_demo.jpg"

headers = {'Ocp-Apim-Subscription-Key': subscription_key, }

data = {'url': image_url}
response = requests.post(
    text_recognition_url, headers=headers, json=data
)
response.raise_for_status()
print(response)
operation_url = response.headers["Operation-Location"]

analysis = {}
poll = True
while poll:
    response_final = requests.get(
        response.headers["Operation-Location"], headers=headers)
    analysis = response_final.json()

    print(json.dumps(analysis, indent=4))

    time.sleep(1)
    if "analyzeResult" in analysis:
        poll = False
    if "status" in analysis and analysis['status'] == 'failed':
        poll = False

polygons = []
if "analyzeResult" in analysis:
    polygons = [(line["boundingBox"], line["text"])
                for line in analysis["analyzeResult"]["readResults"][0]["lines"]]

image = Image.open(BytesIO(requests.get(image_url).content))
ax = plt.imshow(image)
for polygon in polygons:
    vertices = [(polygon[0][i], polygon[0][i + 1])
                for i in range(0, len(polygon[0]), 2)]
    text = polygon[1]
    patch = Polygon(vertices, closed=True, fill=False, linewidth=2, color='y')
    #ax.axes.add_patch(patch)
    plt.text(vertices[0][0], vertices[0][1], text, fontsize=8, va="center")
plt.show()
