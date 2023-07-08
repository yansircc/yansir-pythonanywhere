from client import RestClient
import os

def serp_scraper(query : str, query_amount : int):
    client = RestClient(os.getenv("DFS_ADMIN_EMAIL"), os.getenv("DFS_API_KEY"))
    post_data = dict()
    # You can set only one task at a time
    post_data[len(post_data)] = dict(
        language_code="en",
        location_name="New York Mills,Minnesota,United States",
        keyword=query,
        device="mobile",
        os="ios",
        depth=query_amount,
        max_crawl_pages=1,
    )
    response = client.post("/v3/serp/google/organic/live/regular", post_data)
    # you can find the full list of the response codes here https://docs.dataforseo.com/v3/appendix/errors
    if response["status_code"] == 20000:
        items = response["tasks"][0]["result"][0]["items"]
        titles = []
        # featured_snippet = None
        for item in items:
            if item["type"] == "organic":
                titles.append(f'[rank: {item["rank_group"]}, url: {item["url"]}, title: {item["title"]}, desc: {item["description"]}]')
            if item["type"] == "featured_snippet":
                pass
        return titles
    else:
        print("error. Code: %d Message: %s" % (response["status_code"], response["status_message"]))