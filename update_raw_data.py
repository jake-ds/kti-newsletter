import pandas as pd
import json


def process_csv(input_file, output_file_managers, output_file_companies):
    # CSV 파일 읽기
    df = pd.read_csv(input_file)

    # 담당자별 관리 회사 생성
    manager_company_map = {}
    for _, row in df.iterrows():
        managers = row["담당자"].split("/")  # 담당자가 여러 명일 경우 분리
        company = row["기업명"]
        for manager in managers:
            manager = manager.strip()  # 공백 제거
            if manager not in manager_company_map:
                manager_company_map[manager] = []
            if company not in manager_company_map[manager]:
                manager_company_map[manager].append(company)

    # JSON 파일로 저장 (담당자별 관리 회사)
    with open(output_file_managers, "w", encoding="utf-8") as f:
        json.dump(manager_company_map, f, ensure_ascii=False, indent=4)

    # 회사별 키워드 및 회사소개 생성
    company_data = {}
    for _, row in df.iterrows():
        company = row["기업명"]
        keyword = row["키워드"]
        intro = row["회사소개"]

        if company not in company_data:
            company_data[company] = {
                "keyword": [],
                "comment": intro,  # 회사소개를 코멘트로 사용
            }
        if keyword and keyword not in company_data[company]["keyword"]:
            company_data[company]["keyword"].append(keyword)

    # JSON 파일로 저장 (회사별 키워드 및 코멘트)
    with open(output_file_companies, "w", encoding="utf-8") as f:
        json.dump(company_data, f, ensure_ascii=False, indent=4)

    print("두 개의 파일이 성공적으로 생성되었습니다.")


# 함수 실행 예제
input_file = "portfolio_news_data.csv"  # 제공된 CSV 파일 경로
output_file_managers = "manager_company_map.json"
output_file_companies = "company_keyword_comment.json"

process_csv(input_file, output_file_managers, output_file_companies)
