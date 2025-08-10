FEEDBACK_GENERATION_PROMPT = """
학습 주제: {lessons}
학습자 요약: {summary}

위 요약에 대해 다음 JSON 형식으로 피드백을 제공해주세요:

{{
  "comment": "구체적인 피드백 내용",
  "score": 8.5
}}

제약 조건:
- score는 0.0~10.0 사이의 숫자
- comment는 건설적이고 구체적인 조언
- JSON 형식만 응답하세요
"""
