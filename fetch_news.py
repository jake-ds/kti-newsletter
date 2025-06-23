import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import random
import asyncio
import json
from playwright.async_api import async_playwright


def get_search_interval():
    current_time = datetime.now()
    one_day_ago = current_time - timedelta(days=1)
    current_time_str = current_time.strftime("%Y.%m.%d.%H.%M")
    one_day_ago_str = one_day_ago.strftime("%Y.%m.%d.%H.%M")
    return current_time_str, one_day_ago_str


def make_target_url(search_keyword):
    date_end, date_start = get_search_interval()
    target_url = (
        f"https://search.naver.com/search.naver?where=news&query=%22{search_keyword}%22"
        f"&sm=tab_opt&sort=0&photo=0&field=0&pd=4&ds={date_start}&de={date_end}"
        f"&docid=&related=0&mynews=0&office_type=0&office_section_code=0"
        f"&news_office_checked=&nso=so%3Ar%2Cp%3A1d&is_sug_officeid=0&office_category=0"
        f"&service_area=0"
    )
    return target_url


async def fetch_html(url: str) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")  # JS 렌더링 끝까지 대기
        html = await page.content()
        await browser.close()
        return html


async def fetch_news(target_url):
    # User-Agent 목록
    html = await fetch_html(target_url)
    soup = BeautifulSoup(html, "html.parser")

    articles = []
    for card in soup.select("div.sds-comps-base-layout"):
        # 제목(span 에 headline1 클래스 포함)
        title_span = card.select_one("span.sds-comps-text-type-headline1")
        if not title_span:
            continue  # 제목 없으면 뉴스 카드로 보지 않음

        title = title_span.get_text(" ", strip=True)
        link = title_span.find_parent("a")["href"]

        # 내용(span 에 ellipsis-3 클래스 포함)
        content_span = card.select_one("span.sds-comps-text-ellipsis-3")
        content = content_span.get_text(" ", strip=True) if content_span else ""
        articles.append((title, content, link))
    return articles
