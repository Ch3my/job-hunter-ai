import http.client
import json
from functions import load_config
import urllib.parse

def build_search_url():
    config = load_config()
    base_url = "/search_jobs"
    params = {}

    if config.get("jobQuery"):
        params["query"] = config["jobQuery"]

    if config.get("jobLocation"):
        params["location"] = config["jobLocation"]

    if config.get("jobPlace"):
        params["workplaceType"] = config["jobPlace"]

    # Add default parameters
    params["page"] = "1"
    params["easyApply"] = "false"

    # Construct the URL
    url = base_url + "?" + urllib.parse.urlencode(params)
    return url

def get_jobs():
    config = load_config()
    conn = http.client.HTTPSConnection("linkedin-data-scraper.p.rapidapi.com")
    # x-rapidapi-key in config
    headers = {
        "x-rapidapi-key": config["rapidApiKey"],
        "x-rapidapi-host": "linkedin-data-scraper.p.rapidapi.com",
    }
    # Build url with config
    url = build_search_url()

    conn.request("GET", url, headers=headers)
    res = conn.getresponse()
    data = res.read()
    json_data = json.loads(data.decode("utf-8"))

    return json_data["response"]
