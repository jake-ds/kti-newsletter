import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import random

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


def fetch_news(target_url):


    # User-Agent 목록
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64)  AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)  AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X)  AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
    ]

    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
}
    
    try:
        response = requests.get(target_url, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching news: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    articles = []

    for item in soup.find_all('div', class_='news_area'):
        title_tag = item.find('a', class_='news_tit')
        desc_tag = item.find('div', class_='news_dsc')

        if title_tag and desc_tag:
            title = title_tag.get('title', '').strip()
            description = desc_tag.get_text(strip=True)
            url = title_tag.get('href', '').strip()
            articles.append((title, description, url))

    return articles
