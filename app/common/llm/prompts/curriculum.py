CURRICULUM_GENERATION_PROMPT = """
목표: {goal}
기간(주): {period}
난이도: {difficulty}
세부요청: {details}
**제약 조건:**
- `lessons` 항목은 각 주차별 최소 1개, 최대 5개의 문자열 리스트여야 합니다.
- 실용적이고 구체적인 내용으로 구성하시오

IMPORTANT: 반드시 유효한 JSON만 응답하세요. 다른 텍스트는 포함하지 마세요.
Output raw JSON only, without any markdown or fences.

다음 JSON 형식으로 커리큘럼을 생성해주세요:
{{
  "title": "<커리큘럼 제목>",
  "schedule": [
    {{ "week_number": 1, "lessons": ["Intro","Setup"] }},
    …,
    {{ "week_number": {period}, "lessons": ["…","…"] }}
  ]
}}
"""
