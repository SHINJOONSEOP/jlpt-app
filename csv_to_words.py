# csv_to_words.py
# OpenAI API 로 한국어 번역 + 예문 생성
# 사용법: python csv_to_words.py 입력파일.csv

import csv
import sys
import os
import json
import time
import requests
import re

# ══════════════════════════════════════════
#   ★ 여기에 OpenAI API 키 입력 ★
API_KEY = "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"
# 발급: https://platform.openai.com/api-keys
# ══════════════════════════════════════════

API_URL    = "https://api.openai.com/v1/chat/completions"
MODEL      = "gpt-3.5-turbo"
BATCH_SIZE = 10    # 예문 생성 포함이라 작게
MAX_RETRY  = 3

def is_korean(text):
    return bool(re.search(r'[가-힣]', text))

def extract_json(text):
    """텍스트에서 JSON 배열/객체 추출"""
    # ```json ... ``` 블록 제거
    text = re.sub(r'```(?:json)?', '', text).replace('```', '').strip()
    # [ ] 배열 추출
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if match:
        return match.group(0)
    return text

def call_gpt(messages, max_tokens=2000):
    """GPT API 호출"""
    res = requests.post(
        API_URL,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type" : "application/json"
        },
        json={
            "model"      : MODEL,
            "messages"   : messages,
            "temperature": 0.3,
            "max_tokens" : max_tokens
        },
        timeout=60
    )
    data = res.json()
    if "error" in data:
        raise Exception(data["error"]["message"])
    return data["choices"][0]["message"]["content"].strip()

def translate_and_generate_batch(batch, retry=0):
    """
    배치 단어 목록에 대해 한번에:
    - 한국어 번역
    - 일본어 예문
    - 한국어 예문
    생성
    """
    words_info = []
    for w in batch:
        words_info.append({
            "japanese": w["japanese"],
            "furigana": w["furigana"],
            "english" : w["english"]
        })

    prompt = f"""다음 일본어 단어들에 대해 아래 작업을 해주세요:
1. 영어 뜻을 자연스러운 한국어로 번역 (10자 이내)
2. 단어를 활용한 짧은 일본어 예문 생성 (15자 이내, 히라가나/한자 혼용)
3. 해당 예문의 한국어 번역

입력 데이터:
{json.dumps(words_info, ensure_ascii=False, indent=2)}

반드시 아래 JSON 배열 형식으로만 반환하세요 (다른 텍스트 절대 금지):
[
  {{
    "japanese"  : "원래 일본어 단어",
    "korean"    : "한국어 뜻",
    "example_jp": "일본어 예문。",
    "example_kr": "한국어 예문 번역."
  }},
  ...
]"""

    try:
        text   = call_gpt([
            {
                "role"   : "system",
                "content": "You are a Japanese-Korean language expert. Return only valid JSON arrays."
            },
            {
                "role"   : "user",
                "content": prompt
            }
        ])

        result = json.loads(extract_json(text))

        # 검증
        if not isinstance(result, list):
            raise ValueError("배열이 아님")
        if len(result) != len(batch):
            raise ValueError(f"개수 불일치: {len(result)} vs {len(batch)}")

        # 각 항목 한국어 포함 여부 확인
        for item in result:
            if not is_korean(item.get("korean", "")):
                raise ValueError(f"한국어 번역 없음: {item}")

        return result

    except Exception as e:
        if retry < MAX_RETRY:
            time.sleep(1.5)
            return translate_and_generate_batch(batch, retry + 1)
        # 최종 실패 → 단어별 개별 처리
        return [translate_single(w) for w in batch]


def translate_single(w):
    """단어 1개 개별 처리 (배치 실패 시 폴백)"""
    prompt = f"""일본어 단어 정보:
단어: {w['japanese']} ({w['furigana']})
영어 뜻: {w['english']}

아래를 JSON 객체로 반환하세요:
{{
  "japanese"  : "{w['japanese']}",
  "korean"    : "한국어 뜻 (10자 이내)",
  "example_jp": "이 단어를 쓴 짧은 일본어 예문。",
  "example_kr": "예문의 한국어 번역."
}}
JSON 객체만 반환, 다른 텍스트 금지."""

    try:
        text   = call_gpt([{"role": "user", "content": prompt}], max_tokens=200)
        # { } 객체 추출
        match  = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            result = json.loads(match.group(0))
            if is_korean(result.get("korean", "")):
                return result
    except Exception:
        pass

    # 완전 실패 시 기본값
    return {
        "japanese"  : w["japanese"],
        "korean"    : w["english"],
        "example_jp": f"{w['japanese']}。",
        "example_kr": f"{w['english']}."
    }


def convert(input_file, output_file="words.py"):

    # ── CSV 읽기 ──────────────────────────────
    rows    = []
    skipped = 0

    with open(input_file, "r", encoding="utf-8-sig") as f:
        for i, row in enumerate(csv.reader(f), 1):
            if not row or all(c.strip() == "" for c in row):
                skipped += 1
                continue
            if len(row) < 4:
                skipped += 1
                continue

            japanese = row[0].strip()
            furigana = row[1].strip()
            english  = row[2].strip().replace('"','').replace("'","")
            level    = row[3].strip().upper()

            if not japanese or not furigana:
                skipped += 1
                continue

            if not level.startswith("N"):
                level = "N" + level
            if level not in ["N1","N2","N3","N4","N5"]:
                level = "N5"

            rows.append({
                "japanese": japanese,
                "furigana": furigana,
                "english" : english,
                "level"   : level,
                "korean"  : english,
                "example_jp": f"{japanese}。",
                "example_kr": f"{english}."
            })

    print(f"\n📖 {len(rows)}개 단어 읽기 완료 (스킵: {skipped}개)")

    if not API_KEY:
        print("\n⚠  API_KEY 없음 → 영어 그대로 저장")
        print("   파일 상단 API_KEY 에 OpenAI 키를 입력하세요")
    else:
        total    = (len(rows) + BATCH_SIZE - 1) // BATCH_SIZE
        est_cost = len(rows) * 80 / 1000 * 0.002
        print(f"\n🔄 GPT 번역 + 예문 생성 시작")
        print(f"   모델      : {MODEL}")
        print(f"   총 단어   : {len(rows)}개")
        print(f"   배치 크기 : {BATCH_SIZE}개씩 → {total}배치")
        print(f"   예상 비용 : 약 ${est_cost:.3f} (약 {int(est_cost*1350)}원)")
        print(f"   예상 시간 : 약 {total * 4}초\n")

        failed_count = 0

        for idx in range(total):
            s     = idx * BATCH_SIZE
            e     = min(s + BATCH_SIZE, len(rows))
            batch = rows[s:e]

            results = translate_and_generate_batch(batch)

            for i, res in enumerate(results):
                row = rows[s + i]
                row["korean"]     = res.get("korean", row["english"])
                row["example_jp"] = res.get("example_jp", f"{row['japanese']}。")
                row["example_kr"] = res.get("example_kr", f"{row['korean']}.")

                if not is_korean(row["korean"]):
                    failed_count += 1

            pct = int((idx + 1) / total * 100)
            bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
            print(f"\r  [{bar}] {pct}%  ({e}/{len(rows)}개 완료)", end="", flush=True)

            if idx < total - 1:
                time.sleep(0.5)

        print(f"\n\n✅ 완료! (미번역: {failed_count}개)")

    # ── words.py 저장 ─────────────────────────
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# words.py\n# 총 {len(rows)}개 단어\n\nWORDS = [\n")

        for w in rows:
            jp     = w["japanese"].replace("\\","\\\\").replace('"','\\"')
            fu     = w["furigana"].replace("\\","\\\\").replace('"','\\"')
            kr     = w["korean"].replace("\\","\\\\").replace('"','\\"')
            ex_jp  = w["example_jp"].replace("\\","\\\\").replace('"','\\"')
            ex_kr  = w["example_kr"].replace("\\","\\\\").replace('"','\\"')
            lv     = w["level"]

            f.write(f'''    {{
        "japanese"  : "{jp}",
        "furigana"  : "{fu}",
        "korean"    : "{kr}",
        "example_jp": "{ex_jp}",
        "example_kr": "{ex_kr}",
        "level"     : "{lv}",
    }},\n''')

        f.write("]\n")

    print(f"📄 {output_file} 저장 완료!\n")

    # ── 통계 ──────────────────────────────────
    from collections import Counter
    lc       = Counter(w["level"] for w in rows)
    kr_count = sum(1 for w in rows if is_korean(w["korean"]))
    ex_count = sum(1 for w in rows if is_korean(w["example_kr"]))

    print("📊 레벨별 통계:")
    for lv in ["N1","N2","N3","N4","N5"]:
        cnt = lc.get(lv, 0)
        bar = "█" * min(cnt // 50, 40)
        print(f"  {lv}: {cnt:5d}개  {bar}")
    print(f"\n  합계          : {len(rows)}개")
    print(f"  한국어 번역   : {kr_count}개")
    print(f"  한국어 예문   : {ex_count}개")
    print(f"  미번역        : {len(rows) - kr_count}개")


# ── 실행 ──────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""
╔══════════════════════════════════════════╗
║  CSV → words.py 변환기                   ║
║  GPT 한국어 번역 + 예문 자동 생성        ║
╚══════════════════════════════════════════╝

사용법:
  python csv_to_words.py 입력.csv
  python csv_to_words.py 입력.csv 출력.py

CSV 형식 (4컬럼):
  한자, 히라가나, 영어뜻, 레벨
  分かる, わかる, to understand, N5

API 키 설정:
  파일 상단 API_KEY = "" 에 입력
  발급: https://platform.openai.com/api-keys

예상 비용 (gpt-3.5-turbo):
  1,000개 → 약 $0.16 (약 216원)
  5,000개 → 약 $0.80 (약 1080원)
  8,000개 → 약 $1.28 (약 1728원)
""")
        sys.exit(1)

    input_file  = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) >= 3 else "words.py"

    if not os.path.exists(input_file):
        print(f"❌ 파일 없음: {input_file}")
        sys.exit(1)

    print(f"📂 {input_file} 읽는 중...")
    convert(input_file, output_file)