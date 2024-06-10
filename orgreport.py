import pymongo
from openai import OpenAI
from datetime import datetime, timedelta
import time

# OpenAI API Key
client = OpenAI(
    api_key="sk-proj-gQzWO1s8RcfOAU5MjknsT3BlbkFJqjdnxsA4MEFKIZHfleBf"
)

# MongoDB Atlas connection
mongo_client = pymongo.MongoClient('mongodb://syonb:syonsmart@ac-0w6souu-shard-00-00.jfanqj5.mongodb.net:27017,ac-0w6souu-shard-00-01.jfanqj5.mongodb.net:27017,ac-0w6souu-shard-00-02.jfanqj5.mongodb.net:27017/?replicaSet=atlas-yytbi1-shard-0&ssl=true&authSource=admin')
db = mongo_client['test']
collection = db['organizations']

# Function to format data for the vulnerability report
def format_report_data(doc):
    formatted_data = {
        "organizationName": doc.get("organizationName"),
        "numUsers": len(doc.get("usernames", [])),
        "endpoints": [],
        "vulnerability_log": doc.get("vulnerability_log", [])[-4:]  # Latest 4 logs
    }

    for endpoint in doc.get("endpoints", []):
        endpoint_data = {
            "startDate": endpoint.get("startDate"),
            "items": []
        }
        
        for item in endpoint.get("items", []):
            item_data = {
                "description": item.get("description"),
                "service": item.get("service"),
                "url": item.get("url"),
                "scan": item.get("scan"),
                "results": {}
            }

            for key, result in item.get("results", {}).items():
                result_data = result.copy()
                if item.get("service") == "Domain":
                    result_data["Paths"] = len(result.get("Paths", []))
                item_data["results"][key] = result_data

            endpoint_data["items"].append(item_data)
        
        formatted_data["endpoints"].append(endpoint_data)

    return formatted_data

# Function to create a report using OpenAI
def create_vulnerability_report(data):
    try:
        prompt = (
            f"Generate a detailed vulnerability report using this data, "
            f"keep in mind that the endpoint phishing tests are run by the company, "
            f"OSINT tests are also run by the company along with network and domain scans that are run by the company: "
            f"{data}. In this strict format and don't include N/A fields in the result: "
            f"Scope: Summary: Findings: Recommendations: Conclusion:"
        )
        print(f"Sending prompt to OpenAI:\n{prompt}")
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a security analyst creating a vulnerability report."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1024
        )

        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in generating report: {e}")
        return None

# Function to generate and save reports
def generate_and_save_reports():
    while True:  # Run continuously
        # Fetch all documents
        documents = collection.find()

        for doc in documents:
            last_scan_date = doc.get("date")
            today = datetime.now()
            should_generate_report = False

            # Check if the document already has a report
            if 'vulnerability_report' not in doc or not doc['vulnerability_report'] or not last_scan_date:
                # No report exists, or no last scan date recorded
                should_generate_report = True
            else:
                # Check if the report is 7 days old
                last_scan_datetime = datetime.strptime(last_scan_date, "%Y-%m-%d")
                if (today - last_scan_datetime).days >= 7:
                    should_generate_report = True

            if should_generate_report:
                # Format the data for the vulnerability report
                formatted_data = format_report_data(doc)
                
                # Create the vulnerability report
                report = create_vulnerability_report(formatted_data)

                if report:
                    print(f"Vulnerability Report for {doc['organizationName']}:\n{report}")
                    # Update the document in MongoDB with the new report and scan date
                    collection.update_one(
                        {'_id': doc['_id']},
                        {'$set': {
                            'date': today.strftime("%Y-%m-%d"),
                            'vulnerability_report': report,
                        }}
                    )
                else:
                    print("Failed to generate report.")
            else:
                print(f"No new report needed for {doc['organizationName']}.")

        # Brief delay before checking again
        time.sleep(60)  # Checks every minute, adjust as needed

# Run the report generation
generate_and_save_reports()
