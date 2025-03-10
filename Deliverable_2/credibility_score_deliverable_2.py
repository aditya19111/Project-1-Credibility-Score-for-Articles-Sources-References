# -*- coding: utf-8 -*-
"""
#Deliverable-2
Student - Aditya Bhavsar
"""

import requests
import tldextract
from datetime import datetime
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline
import time
from textstat import flesch_reading_ease
import os

class CredibilityScorer:
    def __init__(self, hf_token, serp_api_key):
        self.hf_token = hf_token
        self.serp_api_key = serp_api_key
        os.environ["HF_TOKEN"] = hf_token
        self.model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
        self.sentiment_pipeline = pipeline("text-classification", model="nlptown/bert-base-multilingual-uncased-sentiment")

    def get_domain_trust(self, url):
        domain = tldextract.extract(url).registered_domain
        try:
            tranco_response = requests.get("https://tranco-list.eu/top-1m.csv").text
            if domain in tranco_response:
                tranco_rank = tranco_response.split(domain)[0].strip().split("\n")[-1]
                tranco_score = max(100 - (int(tranco_rank) / 10000), 50)
            else:
                tranco_score = 40
        except:
            tranco_score = 40

        try:
            whois_response = requests.get(f"https://api.ip2whois.com/v2?key=demo&domain={domain}").json()
            creation_date = whois_response.get("created_date", "2000-01-01")
            domain_age = (datetime.now() - datetime.strptime(creation_date, "%Y-%m-%d")).days // 365
            age_score = min(domain_age * 5, 100)
        except:
            age_score = 50

        try:
            search = requests.get(f"https://serpapi.com/search.json?q={domain}&api_key={self.serp_api_key}").json()
            backlink_count = len(search.get("organic_results", []))
            backlink_score = min(backlink_count * 10, 100)
        except:
            backlink_score = 50

        domain_trust = (0.4 * tranco_score) + (0.3 * age_score) + (0.3 * backlink_score)
        return round(domain_trust, 2)

    def get_fact_check_score(self, text):
        try:
            params = {
                "q": f"fact check {text}",
                "engine": "google",
                "api_key": self.serp_api_key
            }
            response = requests.get("https://serpapi.com/search", params=params)
            data = response.json()
            trusted_sources = ["snopes.com", "politifact.com", "factcheck.org", "bbc.com", "reuters.com"]
            source_mentions = sum(1 for result in data.get("organic_results", [])
                                  if any(domain in result.get("link", "") for domain in trusted_sources))
            fact_check_score = min(source_mentions * 20, 100)
        except Exception:
            fact_check_score = 50

        try:
            wiki_response = requests.get(
                f"https://en.wikipedia.org/w/api.php?action=query&format=json&list=search&srsearch={text}"
            )
            wiki_data = wiki_response.json()
            wiki_matches = len(wiki_data.get("query", {}).get("search", []))
            fact_check_score += min(wiki_matches * 10, 30)
        except Exception:
            pass

        try:
            trusted_texts = " ".join([
                result["title"] + result["snippet"]
                for result in data.get("organic_results", [])
                if "title" in result and "snippet" in result
            ])
            similarity_score = util.pytorch_cos_sim(
                self.model.encode(text), self.model.encode(trusted_texts)
            ).item() * 100
            fact_check_score += min(similarity_score / 2, 30)
        except Exception:
            pass

        return max(0, min(fact_check_score, 100))

    def get_bias_score(self, text, domain):
        sentiment_result = self.sentiment_pipeline(text[:512])[0]
        sentiment_bias = {
            "1 star": 30,
            "2 stars": 50,
            "3 stars": 70,
            "4 stars": 80,
            "5 stars": 100
        }
        bias_score = sentiment_bias.get(sentiment_result["label"], 50)
        try:
            bias_response = requests.get(f"https://api.allsides.com/bias/{domain}").json()
            media_bias = bias_response.get("bias", "center")
            bias_adjustment = {
                "left": -20,
                "lean left": -10,
                "center": 0,
                "lean right": 10,
                "right": 20
            }.get(media_bias.lower(), 0)
            bias_score = max(0, min(bias_score + bias_adjustment, 100))
        except:
            pass
        return round(bias_score, 2)

    def compute_content_relevance(self, user_query, page_text):
        similarity_score = util.pytorch_cos_sim(
            self.model.encode(user_query), self.model.encode(page_text)
        ).item() * 100
        return round(similarity_score, 2)

    def check_google_scholar(self, url):
        try:
            backlink_params = {
                "q": f"link:{url}",
                "engine": "google",
                "api_key": self.serp_api_key
            }
            backlink_response = requests.get("https://serpapi.com/search", params=backlink_params).json()
            backlink_count = len(backlink_response.get("organic_results", []))

            academic_params = {
                "q": f'"{url}" filetype:pdf OR site:researchgate.net OR site:arxiv.org OR site:semanticscholar.org',
                "engine": "google",
                "api_key": self.serp_api_key
            }
            academic_response = requests.get("https://serpapi.com/search", params=academic_params).json()
            academic_count = len(academic_response.get("organic_results", []))

            citation_score = min((backlink_count * 5) + (academic_count * 15), 100)
            return round(citation_score, 2)
        except Exception as e:
            print(f"Error fetching citation data: {e}")
            return 0

    def get_page_load_speed(self, url):
        start_time = time.time()
        try:
            response = requests.get(url, timeout=10)
            load_time = time.time() - start_time
            return max(0, min(100 - (load_time * 10), 100))
        except:
            return 50

    def check_plagiarism(self, text):
        try:
            search_query = f'"{text[:100]}"'
            response = requests.get(f"https://serpapi.com/search?q={search_query}&api_key={self.serp_api_key}")
            duplicate_results = len(response.json().get("organic_results", []))
            return max(0, 100 - (duplicate_results * 20))
        except:
            return 50

    def get_readability_score(self, text):
        try:
            score = flesch_reading_ease(text)
            return max(0, min(score, 100))
        except:
            return 50

    def check_ssl_security(self, url):
        try:
            domain = tldextract.extract(url).registered_domain
            response = requests.get(f"https://{domain}", timeout=5)
            return 100 if response.url.startswith("https") else 0
        except:
            return 0

    def check_language_complexity(self, text):
        try:
            coherence_score = util.pytorch_cos_sim(self.model.encode(text[:500]), self.model.encode("High-quality journalistic content.")).item() * 100
            return round(coherence_score, 2)
        except:
            return 50

    def get_user_engagement(self, url):
        try:
            response = requests.get(f"https://serpapi.com/search?q=site:{url}&api_key={self.serp_api_key}")
            social_mentions = len(response.json().get("organic_results", []))
            return min(social_mentions * 10, 100)
        except:
            return 50

    def get_star_rating(self, score: float) -> tuple:
        stars = max(1, min(5, round(score / 20)))
        return stars, "⭐" * stars

    def generate_explanation(self, metrics: dict, final_score: float) -> str:
        reasons = []
        if metrics.get("Domain Trust", 0) < 50:
            reasons.append("The source has low domain authority.")
        if metrics.get("Content Relevance", 0) < 50:
            reasons.append("The content is not highly relevant to your query.")
        if metrics.get("Fact-Check Score", 0) < 50:
            reasons.append("Limited fact-checking verification found.")
        if metrics.get("Bias Score", 0) < 50:
            reasons.append("Potential bias detected in the content.")
        if metrics.get("Citation Score", 0) < 30:
            reasons.append("Few citations found for this content.")
        if metrics.get("Page Load Speed Score", 0) < 50:
            reasons.append("The page load speed is slow.")
        if metrics.get("Plagiarism Score", 0) < 50:
            reasons.append("High similarity to other sources detected.")
        if metrics.get("Readability Score", 0) < 50:
            reasons.append("The content is difficult to read.")
        if metrics.get("SSL Security Score", 0) < 50:
            reasons.append("The website may not be secure.")
        if metrics.get("Language Coherence Score", 0) < 50:
            reasons.append("The language coherence is below expectations.")
        if metrics.get("User Engagement Score", 0) < 50:
            reasons.append("Low user engagement detected.")

        if not reasons:
            reasons.append("This source is highly credible and relevant.")

        explanation = " ".join(reasons) + f" Overall credibility score: {round(final_score, 2)}."
        return explanation

    def rate_url_validity(self, user_query: str, url: str) -> dict:
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            page_text = " ".join([p.text for p in soup.find_all("p")])
        except Exception:
            return {"error": "Failed to fetch content."}

        domain = tldextract.extract(url).registered_domain

        # Compute each metric
        domain_trust       = self.get_domain_trust(url)
        content_relevance  = self.compute_content_relevance(user_query, page_text)
        fact_check_score   = self.get_fact_check_score(page_text)
        bias_score         = self.get_bias_score(page_text, domain)
        citation_score     = self.check_google_scholar(url)
        page_load_speed    = self.get_page_load_speed(url)
        plagiarism_score   = self.check_plagiarism(page_text)
        readability_score  = self.get_readability_score(page_text)
        ssl_security       = self.check_ssl_security(url)
        language_coherence = self.check_language_complexity(page_text)
        user_engagement    = self.get_user_engagement(url)

        # Detailed final score calculation using all metrics and weights
        final_score_detailed = (
            (0.10 * domain_trust) +
            (0.50 * content_relevance) +
            (0.05 * fact_check_score) +
            (0.05 * bias_score) +
            (0.10 * citation_score) +
            (0.05 * page_load_speed) +
            (0.05 * plagiarism_score) +
            (0.025 * readability_score) +
            (0.03 * ssl_security) +
            (0.02 * language_coherence) +
            (0.025 * user_engagement)
        )

        # Gather metrics into a dictionary
        metrics = {
            "Domain Trust": domain_trust,
            "Content Relevance": content_relevance,
            "Fact-Check Score": fact_check_score,
            "Bias Score": bias_score,
            "Citation Score": citation_score,
            "Page Load Speed Score": page_load_speed,
            "Plagiarism Score": plagiarism_score,
            "Readability Score": readability_score,
            "SSL Security Score": ssl_security,
            "Language Coherence Score": language_coherence,
            "User Engagement Score": user_engagement
        }

        # Use detailed score for star rating and explanation
        stars, star_icon = self.get_star_rating(final_score_detailed)
        explanation = self.generate_explanation(metrics, final_score_detailed)

        return {
            "final_score_detailed": round(final_score_detailed, 2),
            "stars": {
                "score": stars,
                "icon": star_icon
            },
            "explanation": explanation
        }

