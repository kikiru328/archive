CURRICULUM_GENERATION_PROMPT = """
목표: {goal}
기간(주): {period}  
난이도: {difficulty}
세부요청: {details}

**중요**: 반드시 주어진 목표({goal})에 맞는 커리큘럼을 생성하세요. 
목표가 애매하더라도 프로그래밍이 아닌 다른 주제일 수 있습니다.

**제약 조건:**
- 주어진 목표에 정확히 맞는 내용으로 구성
- 각 주차별 최소 1개, 최대 5개 레슨
- 실용적이고 구체적인 내용

다음 JSON 형식으로 응답:
{{
  "title": "<목표에 맞는 커리큘럼 제목>",
  "schedule": [
    {{ "week_number": 1, "lessons": ["레슨1","레슨2"] }},
    {{ "week_number": {period}, "lessons": ["레슨1","레슨2"] }}
  ]
}}
"""
