import json

def extract_pdf_urls(data):
    return [item['url'] for item in data if 'url' in item and '.pdf' in item['url']]

# Load the first JSON file
with open('srea_+_portal-202409041720UTC.json', 'r') as file:
    data1 = json.load(file)

# Load the second JSON file
with open('srea_+_portal.json', 'r') as file:
    data2 = json.load(file)
    
pdf_urls_1 = extract_pdf_urls(data1)
pdf_urls_2 = extract_pdf_urls(data2)

# Find the differences: items in data1 but not in data2
diff_1_to_2 = [url for url in pdf_urls_1 if url not in pdf_urls_2]

# Find the differences: URLs in file2 but not in file1
diff_2_to_1 = [url for url in pdf_urls_2 if url not in pdf_urls_1]