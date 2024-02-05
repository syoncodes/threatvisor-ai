import pymongo
import openai
from datetime import datetime, timedelta
import time  # Import the time module

# OpenAI API Key
openai.api_key = "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"

# MongoDB Atlas connection (replace with your details)
client = pymongo.MongoClient('mongodb://syonb:syonsmart@ac-0w6souu-shard-00-00.jfanqj5.mongodb.net:27017,ac-0w6souu-shard-00-01.jfanqj5.mongodb.net:27017,ac-0w6souu-shard-00-02.jfanqj5.mongodb.net:27017/?replicaSet=atlas-yytbi1-shard-0&ssl=true&authSource=admin')
db = client['test']
collection = db['users']

# Function to format data for the vulnerability report
def format_report_data(doc):
    formatted_data = {
        "date": doc.get("date", "N/A"),
        "data": doc.get("data", {}),
        "percentage_change": doc.get("percentage_change", {}),
        "organizationName": doc.get("organizationName", "N/A"),
        # Add other fields as needed
    }
    # Exclude the "Paths" key from the "endpoints" data
    formatted_data["endpoints"] = [{k: v for k, v in endpoint.items() if k != "Paths"} for endpoint in doc.get("endpoints", [])]
    return formatted_data

# Function to create a report using OpenAI
def create_vulnerability_report(data):
    try:
        prompt = f"Generate a very detailed vulnerability report using this data, keep in mind that the endpoint phishing tests are run by the company, OSINT tests are also run by the company along with network and domain scans that are run by the company: {data}. In this strict format and don't include N/A fields in the result: Scope: Summary: Findings: Recommendations: Conclusion:"
        print(f"Sending prompt to OpenAI:\n{prompt}")
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a security analyst creating a vulnerability report."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message['content']
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
