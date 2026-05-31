# csv_to_words.py
# OpenAI API 로 영어 뜻 → 한국어 자동 번역
# 사용법: python csv_to_words.py 입력파일.csv

import csv
import sys
import os
import json
import time
import requests

# ══════════════════════════════════════════
#   ★ 여기에 OpenAI API 키 입력 ★
API_KEY = "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"
# console.anthropic.com 아닌
# platform.openai.com → API keys 에서 발급
# ══════════════════════════════════════════

API_URL    = "https://api.openai.com/v1/chat/completions"
MODEL      = "gpt-3.5-turbo"   # 저렴 + 빠름 ($0.002/1K tokens)
BATCH_SIZE = 30                 # 한 번에 번역할 단어 수

def translate_batch(words_en):
    """영어 뜻 리스트 → 한국어 리스트"""
    if not API_KEY:
        return words_en

    prompt = f"""다음은 일본어 단어의 영어 뜻 목록입니다.
각각을 간결한 한국어로 번역해주세요.
핵심 뜻만 (10자 이내), 번호 없이 JSON 배열로만 반환하세요.

영어 목록:
{json.dumps(words_en, ensure_ascii=False)}

반환 예시: ["이해하다", "잊다", "나", "건너다"]
JSON 배열만 반환, 다른 텍스트 포함 금지."""

    try:
        res = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type" : "application/json"
            },
            json={
                "model"   : MODEL,
                "messages": [
                    {
                        "role"   : "system",
                        "content": "You are a Japanese-Korean translator. Return only JSON arrays."
                    },
                    {
                        "role"   : "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.1   # 일관성 높이기
            },
            timeout=30
        )

        data = res.json()

        # API 오류 확인
        if "error" in data:
            print(f"\n  ⚠ API 오류: {data['error']['message']}")
            return words_en

        text = data["choices"][0]["message"]["content"].strip()

        # ```json 블록 제거
        if "```" in text:
            parts = text.split("```")
            for p in parts:
                p = p.strip()
                if p.startswith("json"):
                    p = p[4:]
                if p.startswith("["):
                    text = p
                    break

        result = json.loads(text.strip())

        if len(result) == len(words_en):
            return result
        else:
            print(f"\n  ⚠ 번역 개수 불일치 ({len(result)} vs {len(words_en)})")
            # 부족한 만큼 영어로 채우기
            while len(result) < len(words_en):
                result.append(words_en[len(result)])
            return result[:len(words_en)]

    except json.JSONDecodeError:
        print(f"\n  ⚠ JSON 파싱 실패, 영어 유지")
        return words_en
    except Exception as e:
        print(f"\n  ⚠ 오류: {e}")
        return words_en


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
                print(f"  ⚠ {i}줄 스킵 (컬럼 부족): {row}")
                skipped += 1
                continue

            japanese = row[0].strip()
            furigana = row[1].strip()
            english  = row[2].strip().replace('"','').replace("'","")
            level    = row[3].strip()

            if not japanese or not furigana:
                skipped += 1
                continue

            # 레벨 정규화
            level = level.upper()
            if not level.startswith("N"):
                level = "N" + level
            if level not in ["N1","N2","N3","N4","N5"]:
                level = "N5"

            rows.append({
                "japanese": japanese,
                "furigana": furigana,
                "english" : english,
                "level"   : level,
            })

    print(f"\n📖 {len(rows)}개 단어 읽기 완료 (스킵: {skipped}개)")

    # ── 번역 ──────────────────────────────────
    if not API_KEY:
        print("\n⚠  API_KEY 가 비어있어요!")
        print("   이 파일 상단 API_KEY = '' 에 OpenAI API 키를 입력하세요")
        print("   발급: https://platform.openai.com/api-keys")
        print("\n   일단 영어 뜻으로 words.py 를 생성합니다...")
        for r in rows:
            r["korean"] = r["english"]
    else:
        total = (len(rows) + BATCH_SIZE - 1) // BATCH_SIZE
        est_cost = len(rows) * 15 / 1000 * 0.002  # 대략적인 비용
        print(f"\n🔄 OpenAI GPT 번역 시작")
        print(f"   모델    : {MODEL}")
        print(f"   총 단어 : {len(rows)}개")
        print(f"   배치 수 : {total}개 배치 × {BATCH_SIZE}단어")
        print(f"   예상 비용: 약 ${est_cost:.3f} (약 {int(est_cost*1350)}원)")
        print(f"   예상 시간: 약 {total * 2}초\n")

        for idx in range(total):
            s     = idx * BATCH_SIZE
            e     = min(s + BATCH_SIZE, len(rows))
            batch = rows[s:e]

            en_list = [r["english"] for r in batch]
            kr_list = translate_batch(en_list)

            for i, kr in enumerate(kr_list):
                rows[s + i]["korean"] = kr

            # 진행 바
            pct = int((idx + 1) / total * 100)
            bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
            print(f"\r  [{bar}] {pct}%  ({e}/{len(rows)}개 완료)", end="", flush=True)

            # API 요청 간격 (과부하 방지)
            if idx < total - 1:
                time.sleep(0.3)

        print("\n\n✅ 번역 완료!")

    # ── words.py 저장 ─────────────────────────
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"# words.py\n# 총 {len(rows)}개 단어\n\nWORDS = [\n")

        for w in rows:
            jp = w["japanese"].replace("\\","\\\\").replace('"','\\"')
            fu = w["furigana"].replace("\\","\\\\").replace('"','\\"')
            kr = w.get("korean", w["english"]).replace("\\","\\\\").replace('"','\\"')
            lv = w["level"]

            f.write(f'''    {{
        "japanese"  : "{jp}",
        "furigana"  : "{fu}",
        "korean"    : "{kr}",
        "example_jp": "{jp}。",
        "example_kr": "{kr}.",
        "level"     : "{lv}",
    }},\n''')

        f.write("]\n")

    print(f"📄 {output_file} 생성 완료!")

    # ── 레벨별 통계 ───────────────────────────
    from collections import Counter
    lc = Counter(w["level"] for w in rows)
    print("\n📊 레벨별 통계:")
    total_words = 0
    for lv in ["N1","N2","N3","N4","N5"]:
        cnt = lc.get(lv, 0)
        total_words += cnt
        bar = "█" * min(cnt // 50, 40)
        print(f"  {lv}: {cnt:5d}개  {bar}")
    print(f"\n  합계: {total_words}개")


# ── 실행 ──────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""
╔══════════════════════════════════════╗
║  CSV → words.py 변환기               ║
║  (OpenAI GPT 자동 번역)              ║
╚══════════════════════════════════════╝

사용법:
  python csv_to_words.py 입력.csv
  python csv_to_words.py 입력.csv 출력.py

CSV 형식 (4컬럼):
  한자, 히라가나, 영어뜻, 레벨
  分かる, わかる, to understand, N5

API 키 설정:
  이 파일 상단 API_KEY = "" 안에 입력
  발급: https://platform.openai.com/api-keys

예상 비용 (gpt-3.5-turbo 기준):
  1000단어 → 약 $0.03 (약 40원)
  8000단어 → 약 $0.24 (약 320원)
""")
        sys.exit(1)

    input_file  = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) >= 3 else "words.py"

    if not os.path.exists(input_file):
        print(f"❌ 파일 없음: {input_file}")
        sys.exit(1)

    print(f"📂 {input_file} 읽는 중...")
    convert(input_file, output_file)