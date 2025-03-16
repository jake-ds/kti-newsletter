from tqdm import tqdm
from data_loader import load_json
from email_sender import format_email_content, send_email
from filter_similar_news import filter_similar_titles
from fetch_news import make_target_url, fetch_news
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Verify environment variables are loaded
required_env_vars = [
    'OPENAI_API_KEY',
    'SMTP_SERVER',
    'SMTP_PORT',
    'EMAIL_LOGIN',
    'EMAIL_PASSWORD'
]

missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
if missing_vars:
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Load configuration files
news_dict = {}
companies = load_json("company_keyword_comment.json")
user_info = load_json("user_info.json")
managed_company = load_json("manager_company_map.json")


def reorder_news_dict(news_dict, user_companies):
    reordered_dict = {}
    for company in user_companies:
        if company in news_dict.keys():
            reordered_dict[company] = news_dict[company]

    for company, _ in news_dict.items():
        if company not in reordered_dict:
            reordered_dict[company] = news_dict[company]

    return reordered_dict

for company, detail in tqdm(companies.items()):
    time.sleep(1.0)
    articles = []
    for keyword in detail["keyword"]:
        target_url = make_target_url(keyword)
        articles += fetch_news(target_url)

    titles = [i[0] for i in articles]
    idx_list = filter_similar_titles(titles)

    filtered_articles = [articles[i] for i in idx_list]

    if len(filtered_articles) != 0:
        news_dict[company] = filtered_articles


# 유저별 뉴스 정렬 후 이메일 발송
for user_name, user_detail in user_info.items():
    user_companies = managed_company.get(user_name, {})
    
    # 테스트 모드일 때는 환경변수의 이메일 주소 사용
    test_email = os.environ.get("RECIPIENTS")
    user_email = [test_email] if test_email else user_info.get(user_name, {}).get("email", [])

    if user_companies:
        reordered_news_dict = reorder_news_dict(news_dict, user_companies)
    else:
        reordered_news_dict = news_dict

    result_dict = {}
    for company, news_list in reordered_news_dict.items():
        result_dict[company] = {"news_list": [], "keyword": []}
        result_dict[company]["news_list"] = news_list
        result_dict[company]["keyword"] = companies[company]["keyword"]

    email_body = format_email_content(result_dict, user_name)
    
    # 테스트 모드일 때 로그 출력
    if test_email:
        print(f"Test mode: Sending email to {test_email}")
    
    send_email(email_body, user_email)
