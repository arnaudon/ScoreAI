import requests
from bs4 import BeautifulSoup
from pprint import pprint
import pandas as pd


def get_works():
    """return a dataframe of works"""
    # TODO: do this once and save in a table
    df = pd.DataFrame()
    for i in range(10):
        print("loading page ", i)
        start = i * 1000
        url = f"https://imslp.org/imslpscripts/API.ISCR.php?account=worklist/disclaimer=accepted/sort=id/type=2/start={start}"
        data = requests.get(url).json()
        data.pop("metadata")
        for i, item in data.items():
            i = int(i) + start
            df.loc[i, "title"] = item["intvals"]["worktitle"]
            df.loc[i, "composer"] = item["intvals"]["composer"]
            df.loc[i, "permlink"] = item["permlink"]
    return df


def get_pdfs(url):
    """return a list of pdf urls"""
    # TODO: show a little dialog to compare pdfs and see which one is better before downloading
    # first from the landing page we go to the pdf page
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a", href=True)
    pdf_landing_pages = [
        l["href"] for l in links if "Special:ImagefromIndex" in l["href"]
    ]

    session = requests.Session()
    cookies = {"imslpdisclaimeraccepted": "yes"}
    pdf_urls = []
    for pdf_landing_page in pdf_landing_pages:
        response = session.get(
            str(pdf_landing_page), cookies=cookies, allow_redirects=True
        )

        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("span", id="sm_dl_wait")
        pdf_urls += [l["data-id"] for l in links]
    return pdf_urls


if __name__ == "__main__":
    df = get_works()
    print(df)
    url = df.loc[10, "permlink"]
    pdf_urls = get_pdfs(url)
    print(pdf_urls)
