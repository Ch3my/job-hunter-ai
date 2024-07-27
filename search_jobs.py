import http.client
import json
from functions import load_config
import urllib.parse

def build_search_url():
    # https://rapidapi.com/mgujjargamingm/api/linkedin-data-scraper
    config = load_config()
    base_url = "/search_jobs"
    params = {}

    if config.get("jobQuery"):
        params["query"] = config["jobQuery"]

    if config.get("jobLocation"):
        params["location"] = config["jobLocation"]

    if config.get("searchLocationId"):
        # Id que linkedin usa, separados por coma
        # puede usar este endpoint para buscar 
        # https://rapidapi.com/mgujjargamingm/api/linkedin-data-scraper/playground/apiendpoint_ff374a23-eedd-41e5-a088-5e973b7cc3e3
        # sino permite parametro de busqueda copiar el JS y correrlo desde devtools desde rapidapi
        params["searchLocationId"] = config["searchLocationId"]

    if config.get("workplaceType"):
        # It could be one more of 1,2,3. 1=On-Site, 2=Remote, 3=Hybrid
        params["workplaceType"] = config["workplaceType"]

    if config.get("sortBy"):
        # Could be either DD ( most recent ) or R ( most relevent )
        params["sortBy"] = config["sortBy"]

    if config.get("jobType"):
        # It could one or more of F,P,C,T,V,I,O. F=Full time, P=Part time, C=Contract, 
        # T=Temporary, V=Volunteer, I=Internship, O=Other.
        params["jobType"] = config["jobType"]

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
