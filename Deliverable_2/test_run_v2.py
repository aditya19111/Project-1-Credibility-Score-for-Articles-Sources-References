from 2_credibility_score_deliverable_2 import *  # Ensure this matches your file name

# Instantiate the CredibilityScorer class with API keys
hf_token = "your_huggingface_token"
serp_api_key = "your_serpapi_key"

scorer = CredibilityScorer(hf_token, serp_api_key)

# Define user prompt and URL to validate
user_query = "Nvidias rtx 5070 new gpu is it really good?"
url_to_check = "https://www.fool.com/investing/2025/02/09/is-nvidia-still-a-millionaire-maker-stock/"

# Run the credibility evaluation
result = scorer.rate_url_validity(user_query, url_to_check)

# Print the results in a readable format
import json
print(json.dumps(result, indent=2))
