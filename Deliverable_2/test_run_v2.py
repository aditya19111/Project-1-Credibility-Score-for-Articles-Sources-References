from deliverable2 import *

# Instantiate the URLValidator class
validator = URLValidator()

# Define user prompt and URL
user_prompt = "I have just been on an international flight, can I come back home to hold my 1-month-old newborn?"
url_to_check = "https://www.mayoclinic.org/healthy-lifestyle/infant-and-toddler-health/expert-answers/air-travel-with-infant/faq-20058539"

# Run the validation
result = validator.rate_url_validity(user_prompt, url_to_check)

# Print the results
import json
print(json.dumps(result, indent=2))