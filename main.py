from tqdm import tqdm
from utils.data_loader import load_json, load_company_info_from_csv
from utils.email_sender import format_email_content, send_email
from utils.filter_similar_news import filter_similar_titles, filter_news_by_relevance
from utils.fetch_news import make_target_url, fetch_news
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Verify environment variables are loaded
required_env_vars = [
    "GEMINI_API_KEY",
    "SMTP_SERVER",
    "SMTP_PORT",
    "EMAIL_LOGIN",
    "EMAIL_PASSWORD",
]

missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
if missing_vars:
    raise EnvironmentError(
        f"Missing required environment variables: {', '.join(missing_vars)}"
    )

# Load configuration files
news_dict = {}
company_info = load_company_info_from_csv()
user_info = load_json("user_info.json")


def reorder_news_dict(news_dict, user_companies):
    reordered_dict = {}
    for company in user_companies:
        if company in news_dict.keys():
            reordered_dict[company] = news_dict[company]

    for company, _ in news_dict.items():
        if company not in reordered_dict:
            reordered_dict[company] = news_dict[company]

    return reordered_dict


async def main():
    news_count = 0

    # Step 1: 키워드로 뉴스 검색 및 중복 제거
    print("\n=== Step 1: Fetching news and removing duplicates ===")
    for company, detail in tqdm(company_info.items()):
        await asyncio.sleep(1.5)
        articles = []
        for keyword in detail["keyword"][0].split("/"):
            target_url = make_target_url(keyword)
            articles += await fetch_news(target_url)
            await asyncio.sleep(1.5)
            print(company, ":", keyword)

        titles = [i[0] for i in articles]
        idx_list = filter_similar_titles(titles)

        filtered_articles = [articles[i] for i in idx_list]

        if len(filtered_articles) != 0:
            news_dict[company] = filtered_articles
            news_count += len(filtered_articles)

    if news_count == 0:
        print("No news found")
        return

    print(f"\nTotal news after deduplication: {news_count}")

    # Step 2: AI 기반 관련성 필터링
    enable_relevance_filter = os.environ.get("ENABLE_RELEVANCE_FILTER", "true").lower() == "true"
    beta_test_mode = os.environ.get("BETA_TEST_MODE", "false").lower() == "true"

    if enable_relevance_filter:
        print("\n=== Step 2: AI-based relevance filtering ===")
        relevance_threshold = int(os.environ.get("RELEVANCE_THRESHOLD", "6"))
        print(f"Relevance threshold: {relevance_threshold}/10")

        if beta_test_mode:
            print("⚠️  BETA TEST MODE: Low relevance news will be included with warnings")

        # AI 관련성 필터링 적용
        filtered_news_dict = filter_news_by_relevance(
            news_dict,
            company_info,
            threshold=relevance_threshold,
            beta_mode=beta_test_mode
        )

        # 필터링된 결과로 업데이트
        news_dict.clear()
        news_dict.update(filtered_news_dict)

        final_news_count = sum(len(articles) for articles in news_dict.values())
        print(f"\nFinal news count after relevance filtering: {final_news_count}")

        if final_news_count == 0:
            print("No relevant news found after filtering")
            return
    else:
        print("\n=== Step 2: AI relevance filtering is DISABLED ===")
        print("Set ENABLE_RELEVANCE_FILTER=true to enable it")

    # 유저별 뉴스 정렬 후 이메일 발송
    for user_name, user_detail in user_info.items():
        # company_info에서 해당 manager가 담당하는 회사 목록 추출
        user_companies = [
            company for company, info in company_info.items()
            if user_name in info.get("manager", [])
        ]

        # 테스트 모드일 때는 환경변수의 이메일 주소 사용
        test_email = os.environ.get("TEST_EMAIL")
        user_email = (
            [test_email]
            if test_email
            else user_info.get(user_name, {}).get("email", [])
        )

        if user_companies:
            reordered_news_dict = reorder_news_dict(news_dict, user_companies)
        else:
            reordered_news_dict = news_dict

        result_dict = {}
        for company, news_list in reordered_news_dict.items():
            result_dict[company] = {"news_list": [], "keyword": []}
            result_dict[company]["news_list"] = news_list
            result_dict[company]["keyword"] = company_info[company]["keyword"]

        email_body = format_email_content(result_dict, user_name)

        # 테스트 모드일 때 로그 출력
        if test_email:
            print(f"Test mode: Sending email to {test_email}")

        send_email(email_body, user_email)


if __name__ == "__main__":
    asyncio.run(main())
