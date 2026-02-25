"""Imslp scrapping module."""

import json
import logging
import os
import time
from typing import Any

import numpy as np
import requests
from bs4 import BeautifulSoup
from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic_ai import Agent
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool
from sqlalchemy.dialects.postgresql import insert
from sqlmodel import Session, func, select, text

from app.db import engine, get_session
from app.users import get_admin_user
from shared.scores import IMSLP, ScoreBase

MODEL: Any = os.getenv("MODEL", "test")
logger = logging.getLogger(__name__)
progress_tracker = {"status": "idle", "page": 0, "cancel_requested": False}
router = APIRouter(prefix="/imslp", tags=["imslp"])


def get_metadata(response, bypass=False) -> dict:
    """return a dictionary of metadata from the page"""
    if bypass:
        return {}
    soup = BeautifulSoup(response.text, "html.parser")
    gen_info = soup.find("span", id="General_Information")
    if gen_info is None:
        return {}

    table = gen_info.find_next("table")
    if table is None:
        return {}

    data = {}
    for row in table.find_all("tr"):
        header = row.find("th")
        value = row.find("td")
        if header and value:
            key = header.get_text(" ", strip=True)
            val = value.get_text(" ", strip=True)
            data[key] = val
    return data


def get_pdfs(response):
    """return a list of pdf urls"""
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a", href=True)
    pdf_landing_pages = [l["href"] for l in links if "Special:ImagefromIndex" in l["href"]]

    session = requests.Session()
    cookies = {"imslpdisclaimeraccepted": "yes"}
    pdf_urls = []
    for pdf_landing_page in pdf_landing_pages:
        response = session.get(str(pdf_landing_page), cookies=cookies, allow_redirects=True)

        soup = BeautifulSoup(response.text, "html.parser")
        links = soup.find_all("span", id="sm_dl_wait")
        if links:
            pdf_urls += [l["data-id"] for l in links]
        # try redirect
        else:
            response = session.head(str(pdf_landing_page), cookies=cookies, allow_redirects=True)
            pdf_url = response.url
            if pdf_url.endswith("pdf"):
                pdf_urls.append(pdf_url)
            else:
                print(pdf_url)
    print(pdf_urls)
    return pdf_urls


def get_page(start):
    """Get a page of works from IMSLP."""
    url = (
        "https://imslp.org/imslpscripts/API.ISCR.php?account=worklist/"
        f"disclaimer=accepted/sort=id/type=2/start={start}"
    )
    response = requests.get(url, timeout=60)
    data = response.json()
    data.pop("metadata")
    return data


async def fix_entry(entry):
    """Fix missing values in the entry using an agent."""
    agent = Agent(
        MODEL,
        output_type=ScoreBase,
        system_prompt=""" Fix missing values.""",
        tools=[duckduckgo_search_tool()],
    )
    prompt = f"""Find the information about music piece {entry.model_dump_json()},
    use score_metadata or internet search if the information is missing."""
    res = await agent.run(prompt)
    for key, value in res.output.model_dump().items():
        setattr(entry, key, value)


async def add_entry(i, item, session):
    """Add an entry to the database."""
    response = requests.get(item["permlink"], timeout=60)
    metadata = get_metadata(response)
    entry = IMSLP(
        id=int(i),
        title=metadata.get("Work Title", item["intvals"]["worktitle"]),
        composer=metadata.get("Composer", item["intvals"]["composer"]),
        permlink=item["permlink"],
        instrumentation=metadata.get("Instrumentation", ""),
        style=metadata.get("Piece Style", ""),
        period=metadata.get("Composer Time Period Comp. Period", ""),
        year=metadata.get("Year/Date of Composition Y/D of Comp.", ""),
        key=metadata.get("Key", ""),
        score_metadata=json.dumps(metadata),
    )
    await fix_entry(entry)
    stmt = insert(IMSLP).values(entry.model_dump())
    update_columns = {
        col.name: stmt.excluded[col.name]
        for col in IMSLP.metadata.tables["imslp"].columns
        if col.name != "id"
    }
    stmt = stmt.on_conflict_do_update(index_elements=["id"], set_=update_columns)
    session.exec(stmt)
    session.commit()


async def get_works():
    """Get all works from IMSLP."""
    progress_tracker["status"] = "processing"
    with Session(engine) as session:
        for i in range(0, progress_tracker["total"]):
            progress_tracker["page"] = i
            start = int(i * 1000)

            # random sleep time to avoid being blocked
            time.sleep(np.random.uniform(1, 10))
            data = get_page(start)

            # last page, we stop
            if not data:
                break

            # add entries
            for i, item in data.items():
                i = int(i) + start
                await add_entry(i, item, session)

                # cancelled by user
                if progress_tracker["cancel_requested"]:
                    progress_tracker["status"] = "cancelled"
                    return

    progress_tracker["status"] = "completed"


@router.post("/start/{max_pages}", dependencies=[Depends(get_admin_user)])
def update_imslp_database(max_pages: int, background_tasks: BackgroundTasks):
    """Update the Imslp database."""
    background_tasks.add_task(get_works)
    progress_tracker["page"] = 0
    progress_tracker["status"] = "starting"
    progress_tracker["total"] = max_pages
    return {"message": "Task started successfully!"}


@router.post("/progress", dependencies=[Depends(get_admin_user)])
def get_progress():
    """Get the progress of the IMSLP update"""
    return progress_tracker


@router.post("/cancel", dependencies=[Depends(get_admin_user)])
def cancel():
    """Cancel the IMSLP update"""
    progress_tracker["cancel_requested"] = True


@router.get("/stats", dependencies=[Depends(get_admin_user)])
def get_imslp_stats(session: Session = Depends(get_session)):
    """Get IMSLP stats"""
    return {
        "total_works": session.exec(select(func.count()).select_from(IMSLP)).one(),
        "total_composers": session.exec(select(func.count(func.distinct(IMSLP.composer)))).one(),
    }


@router.post("/empty", dependencies=[Depends(get_admin_user)])
def empty(session: Session = Depends(get_session)):
    """Empty the IMSLP table."""
    if session.bind.dialect.name == "postgresql":
        session.execute(text("TRUNCATE TABLE imslp RESTART IDENTITY CASCADE;"))  # pragma: no cover
    else:
        session.execute(text("DELETE FROM imslp;"))
    session.commit()


@router.get("/scores_by_ids")
def get_by_ids(score_ids: str, session: Session = Depends(get_session)):
    """Get scores by ids."""
    # pylint: disable=no-member
    return session.exec(select(IMSLP).where(IMSLP.id.in_(json.loads(score_ids)))).all()
