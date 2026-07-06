import json
import re

file_path = "c:/UDINUS/SEMESTER6/Pemrograman Sisi Server/simple-lms/simple_lms_postman.json"

with open(file_path, 'r') as f:
    data = f.read()

# Replace hardcoded 1 with correct IDs from DB
data = re.sub(r'/courses/1\b', '/courses/13', data)
data = re.sub(r'/sections/1\b', '/sections/74', data)
data = re.sub(r'/lesson/1\b', '/lesson/157', data)
data = re.sub(r'/lessons/1\b', '/lessons/157', data)
# Path 1, Category 1, User 1 are fine because they actually exist in DB.

with open(file_path, 'w') as f:
    f.write(data)

print("Updated Postman collection with dynamic IDs")
