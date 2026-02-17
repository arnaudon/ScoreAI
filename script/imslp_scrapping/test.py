import requests
import json
from tqdm import tqdm
from bs4 import BeautifulSoup
import pandas as pd
from sqlmodel import Field, SQLModel
import os
from sqlmodel import Session, create_engine

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///imslp.db")
bypass_metadata = True 


class IMSLPEntry(SQLModel, table=True):
    """IMSLPEntry model."""

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field()
    composer: str = Field()
    permlink: str = Field()
    score_metadata: str = Field(default="")
    pdf_urls: str = Field(default="")


def init_db():
    """Initialize database."""
    engine = create_engine(DATABASE_URL)
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get database session."""
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_recycle=3600,
        pool_timeout=30,
    )
    with Session(engine) as session:
        yield session


def get_works(max_pages=2, work_per_page=None):
    """return a dataframe of works"""
    # TODO: do this once and save in a table
    df = pd.DataFrame()
    gen_db = get_session()
    session = next(gen_db)
    for i in tqdm(range(max_pages)):
        print("loading page ", i)
        start = i * 1000 + 1e6
        url = f"https://imslp.org/imslpscripts/API.ISCR.php?account=worklist/disclaimer=accepted/sort=id/type=2/start={start}"
        response = requests.get(url)
        data = response.json()
        data.pop("metadata")

        if not len(data):
            # last page
            break
        for i, item in data.items():
            i = int(i) + start
            df.loc[i, "title"] = item["intvals"]["worktitle"]
            df.loc[i, "composer"] = item["intvals"]["composer"]
            df.loc[i, "permlink"] = item["permlink"]
            score_metadata = ""
            pdf_urls = ""
            if not bypass_metadata:
                response = requests.get(item["permlink"])
                score_metadata = get_metadata(response, bypass=bypass_metadata)
                pdf_urls = json.dumps(get_pdfs(response))
                df.loc[i, "score_metadata"] = score_metadata
                df.loc[i, "pdf_urls"] = pdf_urls
            entry = IMSLPEntry(
                id=int(i),
                title=item["intvals"]["worktitle"],
                composer=item["intvals"]["composer"],
                permlink=item["permlink"],
                score_metadata=score_metadata,
                pdf_urls=pdf_urls,
            )
            session.add(entry)
            if work_per_page is not None and  i > work_per_page - 1 + start:
                break
        session.commit()
    try:
        next(gen_db)
    except StopIteration:
        pass
    return df


def get_metadata(response, bypass=False):
    """return a dictionary of metadata from the page"""
    if bypass:
        return ""
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("span", id="General_Information").find_next("table")
    data = {}

    for row in table.find_all("tr"):
        header = row.find("th")
        value = row.find("td")
        if header and value:
            key = header.get_text(" ", strip=True)
            val = value.get_text(" ", strip=True)
            data[key] = val
    return json.dumps(data)


def get_pdfs(response):
    """return a list of pdf urls"""
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
        if links:
            pdf_urls += [l["data-id"] for l in links]
        # try redirect
        else:
            response = session.head(
                str(pdf_landing_page), cookies=cookies, allow_redirects=True
            )
            pdf_url = response.url
            if pdf_url.endswith("pdf"):
                pdf_urls.append(pdf_url)
            else:
                print(pdf_url)
    print(pdf_urls)
    return pdf_urls


if __name__ == "__main__":
    init_db()
    df = get_works(max_pages=260)
    df.to_csv("imslp.csv")
