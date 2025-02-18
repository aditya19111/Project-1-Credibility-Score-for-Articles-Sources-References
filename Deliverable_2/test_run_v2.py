from Credibility_Score_Deliverable_2 import *

# Instantiate the URLValidator class
validator = rate_url_validity()

# Define user prompt and URL
user_prompt = "will amd FSR get better than nvidia dlss 4"
url_to_check = "https://steamcommunity.com/discussions/forum/11/3543798390532636155/"

# Run the validation
result = validator.rate_url_validity(user_prompt, url_to_check)

# Print the results
import json
print(json.dumps(result, indent=2))
