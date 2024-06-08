import pymongo
from pymongo import MongoClient
import random
import string
import openai
from flask import Flask, request, redirect

# MongoDB Atlas connection details
mongo_uri = 'mongodb://syonb:syonsmart@ac-0w6souu-shard-00-00.jfanqj5.mongodb.net:27017,ac-0w6souu-shard-00-01.jfanqj5.mongodb.net:27017,ac-0w6souu-shard-00-02.jfanqj5.mongodb.net:27017/?replicaSet=atlas-yytbi1-shard-0&ssl=true&authSource=admin'
client = MongoClient(mongo_uri)
db = client['test']  # Replace with your database name
organization_collection = db["organizations"] 

# OpenAI API key
api_key = "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" # Replace with y
openai.api_key = api_key

app = Flask(__name__)

def generate_mask():
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(10))

def generate_phishing_email_body(title, description, mask):
    prompt = f"Title: {title}\nDescription: {description}..."
    response = openai.Completion.create(engine="text-davinci-002", prompt=prompt, max_tokens=150)
    email_body = response.choices[0].text.strip()

    tracking_url = f"http://20.169.49.29:5000/track_click/{mask}"  # Server's URL
    email_body_with_link = f"{email_body}\n\nClick here: {tracking_url}"
    return email_body_with_link

@app.route('/track_click/<mask>', methods=['GET'])
def track_click(mask):
    try:
        # Find the organization and endpoint that contains the item with the given mask
        result = organization_collection.update_one(
            {"endpoints.items.maskedLinkMask": mask},
            {"$inc": {"endpoints.$[].items.$[item].uniqueClickCount": 1}},
            array_filters=[{"item.maskedLinkMask": mask}]
        )
        if result.modified_count == 0:
            return "Link not activated or invalid.", 404
        return redirect('https://google.com', code=302)
    except Exception as e:
        print(f"Error updating click count: {e}")
        return "Internal Server Error", 500

if __name__ == "__main__":
    organizations = organization_collection.find({"endpoints.items.service": "Phishing"})

    for org in organizations:
        for endpoint in org["endpoints"]:
            for item in endpoint["items"]:
                if item.get("service") == "Phishing" and (not item.get("emailBody") or item.get("emailBody").strip() == ""):
                    mask = generate_mask()
                    title = item.get("title", "No Title Provided")
                    description = item.get("description", "No Description Provided")
                    phishing_email_body = generate_phishing_email_body(title, description, mask)

                    organization_collection.update_one(
                        {"_id": org["_id"], "endpoints._id": endpoint["_id"], "endpoints.items._id": item["_id"]},
                        {"$set": {
                            "endpoints.$.items.$[elem].emailBody": phishing_email_body,
                            "endpoints.$.items.$[elem].maskedLinkMask": mask,
                            "endpoints.$.items.$[elem].clickCount": 0
                        }},
                        array_filters=[{"elem._id": item["_id"]}]
                    )

    app.run(host='0.0.0.0', port=5000)
