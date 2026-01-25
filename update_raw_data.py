import pandas as pd
import json


def process_csv(input_file, output_file):
    # CSV 파일 읽기
    df = pd.read_csv(input_file)

    # 회사별 정보 생성 (키워드, 코멘트, 담당자 포함)
    company_data = {}
    for _, row in df.iterrows():
        company = row["기업명"]
        keyword = row["키워드"]
        intro = row["회사소개"]
        managers = [m.strip() for m in row["담당자"].split("/")]  # 담당자가 여러 명일 경우 분리

        if company not in company_data:
            company_data[company] = {
                "keyword": [],
                "comment": intro,  # 회사소개를 코멘트로 사용
                "manager": managers,  # 담당자 리스트
            }
        else:
            # 키워드 추가
            if keyword and keyword not in company_data[company]["keyword"]:
                company_data[company]["keyword"].append(keyword)
            # 담당자 추가 (중복 제거)
            for manager in managers:
                if manager not in company_data[company]["manager"]:
                    company_data[company]["manager"].append(manager)

    # JSON 파일로 저장
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(company_data, f, ensure_ascii=False, indent=4)

    print(f"{output_file} 파일이 성공적으로 생성되었습니다.")


# 함수 실행 예제
input_file = "portfolio_news_data.csv"  # 제공된 CSV 파일 경로
output_file = "company_info.json"

process_csv(input_file, output_file)
