"""
Reference:
 - Prompts are from [graphrag](https://github.com/microsoft/graphrag)
"""

GRAPH_FIELD_SEP = "<SEP>"
PROMPTS = {}

PROMPTS[
    "claim_extraction"
] = """-Target activity-
You are an intelligent assistant that helps a human analyst to analyze claims against certain entities presented in a text document.

-Goal-
Given a text document that is potentially relevant to this activity, an entity specification, and a claim description, extract all entities that match the entity specification and all claims against those entities.

-Steps-
1. Extract all named entities that match the predefined entity specification. Entity specification can either be a list of entity names or a list of entity types.
2. For each entity identified in step 1, extract all claims associated with the entity. Claims need to match the specified claim description, and the entity should be the subject of the claim.
For each claim, extract the following information:
- Subject: name of the entity that is subject of the claim, capitalized. The subject entity is one that committed the action described in the claim. Subject needs to be one of the named entities identified in step 1.
- Object: name of the entity that is object of the claim, capitalized. The object entity is one that either reports/handles or is affected by the action described in the claim. If object entity is unknown, use **NONE**.
- Claim Type: overall category of the claim, capitalized. Name it in a way that can be repeated across multiple text inputs, so that similar claims share the same claim type
- Claim Status: **TRUE**, **FALSE**, or **SUSPECTED**. TRUE means the claim is confirmed, FALSE means the claim is found to be False, SUSPECTED means the claim is not verified.
- Claim Description: Detailed description explaining the reasoning behind the claim, together with all the related evidence and references.
- Claim Date: Period (start_date, end_date) when the claim was made. Both start_date and end_date should be in ISO-8601 format. If the claim was made on a single date rather than a date range, set the same date for both start_date and end_date. If date is unknown, return **NONE**.
- Claim Source Text: List of **all** quotes from the original text that are relevant to the claim.

Format each claim as (<subject_entity>{tuple_delimiter}<object_entity>{tuple_delimiter}<claim_type>{tuple_delimiter}<claim_status>{tuple_delimiter}<claim_start_date>{tuple_delimiter}<claim_end_date>{tuple_delimiter}<claim_description>{tuple_delimiter}<claim_source>)

3. Return output in English as a single list of all the claims identified in steps 1 and 2. Use **{record_delimiter}** as the list delimiter.

4. When finished, output {completion_delimiter}

-Examples-
Example 1:
Entity specification: organization
Claim description: red flags associated with an entity
Text: According to an article on 2022/01/10, Company A was fined for bid rigging while participating in multiple public tenders published by Government Agency B. The company is owned by Person C who was suspected of engaging in corruption activities in 2015.
Output:

(COMPANY A{tuple_delimiter}GOVERNMENT AGENCY B{tuple_delimiter}ANTI-COMPETITIVE PRACTICES{tuple_delimiter}TRUE{tuple_delimiter}2022-01-10T00:00:00{tuple_delimiter}2022-01-10T00:00:00{tuple_delimiter}Company A was found to engage in anti-competitive practices because it was fined for bid rigging in multiple public tenders published by Government Agency B according to an article published on 2022/01/10{tuple_delimiter}According to an article published on 2022/01/10, Company A was fined for bid rigging while participating in multiple public tenders published by Government Agency B.)
{completion_delimiter}

Example 2:
Entity specification: Company A, Person C
Claim description: red flags associated with an entity
Text: According to an article on 2022/01/10, Company A was fined for bid rigging while participating in multiple public tenders published by Government Agency B. The company is owned by Person C who was suspected of engaging in corruption activities in 2015.
Output:

(COMPANY A{tuple_delimiter}GOVERNMENT AGENCY B{tuple_delimiter}ANTI-COMPETITIVE PRACTICES{tuple_delimiter}TRUE{tuple_delimiter}2022-01-10T00:00:00{tuple_delimiter}2022-01-10T00:00:00{tuple_delimiter}Company A was found to engage in anti-competitive practices because it was fined for bid rigging in multiple public tenders published by Government Agency B according to an article published on 2022/01/10{tuple_delimiter}According to an article published on 2022/01/10, Company A was fined for bid rigging while participating in multiple public tenders published by Government Agency B.)
{record_delimiter}
(PERSON C{tuple_delimiter}NONE{tuple_delimiter}CORRUPTION{tuple_delimiter}SUSPECTED{tuple_delimiter}2015-01-01T00:00:00{tuple_delimiter}2015-12-30T00:00:00{tuple_delimiter}Person C was suspected of engaging in corruption activities in 2015{tuple_delimiter}The company is owned by Person C who was suspected of engaging in corruption activities in 2015)
{completion_delimiter}

-Real Data-
Use the following input for your answer.
Entity specification: {entity_specs}
Claim description: {claim_description}
Text: {input_text}
Output: """



PROMPTS["community_report"] = """You are an AI assistant that helps a human analyst or product owner to understand groups of credit card products and their benefits.

# Goal
주어진 엔티티 목록과 관계, (선택적으로) 관련 클레임 정보를 바탕으로
"카드 및 혜택 커뮤니티"에 대한 종합 리포트를 작성하시오.

이 커뮤니티는 특정 소비 패턴(예: 편의점/카페/배달, 교통/통신비, 해외/온라인쇼핑 등)이나
비슷한 연회비·실적 구조를 가진 카드/혜택들이 묶인 군집이라고 가정합니다.

리포트는 의사결정자 또는 추천 시스템 설계자가
- 이 커뮤니티에 속한 카드들이 어떤 공통점/차별점이 있는지
- 어떤 사용자에게 유리한지
- 어떤 제한/주의사항이 있는지
를 빠르게 파악할 수 있도록 도와야 합니다.

# Report Structure

리포트에는 다음 섹션이 포함되어야 합니다:

- TITLE:
  이 커뮤니티를 대표하는 이름.
  가능한 경우 대표적인 카드명 또는 주요 혜택 카테고리를 포함하여,
  짧지만 구체적으로 작성하십시오.
  (예: "편의점·카페 위주 생활할인 카드 커뮤니티", "해외/온라인 특화 프리미엄 카드 군" 등)

- SUMMARY:
  커뮤니티에 속한 주요 카드/혜택들의 전체적인 구조,
  공통적인 혜택 패턴(예: 편의점+카페 결합, 배달앱+간편결제 중심 등),
  그리고 이 커뮤니티가 어떤 유형의 사용자에게 적합한지를 요약하십시오.

- IMPACT SEVERITY RATING:
  0~10 사이의 float 점수.
  이 커뮤니티가 "일반 사용자/해당 소비 패턴을 가진 사용자"에게
  얼마나 강력한 추천 후보군이 될 수 있는지를 나타냅니다.
  (값이 높을수록 "추천 우선순위가 높은" 커뮤니티입니다.)

- RATING EXPLANATION:
  위 점수를 부여한 한 줄 설명.
  (예: "편의점·카페·배달앱을 자주 사용하는 20~30대 직장인에게 매우 적합하여 높은 점수 부여")

- DETAILED FINDINGS:
  이 커뮤니티에 대한 5~10개의 핵심 인사이트 리스트.
  각 인사이트는 다음을 포함:
  - summary: 짧은 요약 (예: "편의점·카페 중복 할인 구조", "실적 대비 높은 추가 청구할인 구간")
  - explanation: 두세 문단 이상의 구체적인 설명.
    어떤 카드/혜택/조건들이 연관되어 있고,
    어떤 사용자 프로필에 유리하거나 불리한지,
    주의해야 할 예외(할인 제외, 실적 제외 등)가 무엇인지 서술하십시오.

리포트는 아래 JSON 형식의 문자열이어야 합니다:
    {{
        "title": <report_title>,
        "summary": <executive_summary>,
        "rating": <impact_severity_rating>,
        "rating_explanation": <rating_explanation>,
        "findings": [
            {{
                "summary": <insight_1_summary>,
                "explanation": <insight_1_explanation>
            }},
            {{
                "summary": <insight_2_summary>,
                "explanation": <insight_2_explanation>
            }}
            ...
        ]
    }}

# Grounding Rules
- 주어진 엔티티/관계/클레임 텍스트에 포함되지 않은 내용은 만들지 마십시오.
- 사용자의 일반적인 카드 사용 패턴에 대한 상식적인 언급은 허용되지만,
  구체적인 수치(할인율, 한도 등)는 반드시 입력 데이터에 근거해야 합니다.

# Real Data

Use the following text for your answer. Do not make anything up in your answer.

Text:
```
{input_text}
```

Output:
"""





PROMPTS["entity_extraction"] = """-Goal-
주어진 우리카드(또는 신용/체크카드) 상품 설명 텍스트와 엔티티 타입 목록을 바탕으로,
카드 추천에 필요한 모든 엔티티와 엔티티 간 관계를 식별하시오.

-Steps-
1. 엔티티 추출
다음과 같은 정보를 엔티티로 식별하시오.

- entity_name: 엔티티 이름 (예: 카드의정석2, 우리카드 7CORE, 신용카드, 편의점, 카페, CU, 전월 실적 50만원 이상, 연회비 22,000원, 간편결제 시 할인 제외 등)
- entity_type: 아래 중 하나 [{entity_types}]
  - CARD_NAME: 특정 카드 상품명 (예: 카드의정석2, 우리카드 7CORE 등)
  - CARD_TYPE: 카드 유형 (예: 신용카드, 체크카드, 국내전용, 마스터카드 등)
  - BENEFIT_CATEGORY: 혜택이 제공되는 영역/카테고리 (예: 편의점, 카페, 배달앱, 대중교통, 온라인쇼핑, 해외이용 등)
  - MERCHANT_OR_BRAND: 특정 가맹점/브랜드/제휴사 (예: CU, GS25, 스타벅스, 배달의민족, 네이버페이 등)
  - SPENDING_CONDITION: 실적/사용 조건 (예: 전월 국내외 가맹점 이용실적 50만원 이상, 건당 1만원 이상, 월 3회까지 등)
  - FEE_OR_LIMIT: 연회비, 월/분기/연 할인·적립 한도, 분기별 추가할인 구간 등의 금액/한도 조건 (예: 연회비 22,000원, 월 최대 10,000원 할인, 분기 300만원 이상 5,000원 할인 등)
  - EXCLUSION_RULE: 할인/실적 제외 조건 (예: 무이자할부, 세금/공과금, 간편결제/PG 경유 시 할인 제외, 해외 이용 제외 등)

- entity_description:
  해당 엔티티에 대한 충분히 자세한 설명.
  예를 들어 CARD_NAME이라면 어떤 혜택 구조를 가진 카드인지,
  CARD_TYPE이라면 어떤 유형의 카드인지,
  BENEFIT_CATEGORY라면 어떤 소비 영역을 의미하는지,
  FEE_OR_LIMIT라면 어떤 한도/연회비/혜택 조건을 말하는지 등을 자연어로 서술하시오.

각 엔티티는 아래 형식으로 출력하시오:
("entity"{tuple_delimiter}<entity_name>{tuple_delimiter}<entity_type>{tuple_delimiter}<entity_description>)

2. 관계 추출
1번에서 추출한 엔티티들 중 **서로 명확한 관련성이 있는 쌍**을 모두 찾아 관계를 정의하시오.

관계 유형의 예시는 다음과 같다:
- CARD_NAME ↔ CARD_TYPE: 특정 카드 상품이 어떤 유형(신용/체크/국내전용 등)에 속하는지
- CARD_NAME ↔ BENEFIT_CATEGORY: 특정 카드가 어떤 혜택 카테고리에서 강한지 (예: 카드의정석2 ↔ 편의점)
- CARD_NAME ↔ MERCHANT_OR_BRAND: 특정 카드와 제휴 브랜드/가맹점 관계 (예: 우리카드 7CORE ↔ 스타벅스)
- CARD_NAME ↔ SPENDING_CONDITION: 카드 이용 시 필요한 전월 실적/건당 조건 (예: 우리카드 7CORE ↔ 전월 실적 70만원 이상)
- CARD_NAME ↔ FEE_OR_LIMIT: 카드의 연회비나 월/분기 할인 한도 (예: 카드의정석2 ↔ 연회비 22,000원 / 월 최대 할인 10,000원)
- CARD_NAME ↔ EXCLUSION_RULE: 이 카드에서 혜택이 적용되지 않는 예외 조건 (예: 카드의정석2 ↔ 간편결제/PG 경유 결제는 할인 제외)
- BENEFIT_CATEGORY ↔ SPENDING_CONDITION 또는 FEE_OR_LIMIT:
  특정 혜택 카테고리의 적용 조건이나 한도 (예: 편의점 ↔ 월 최대 5,000원, 전월 50만원 이상 시)
- CARD_NAME ↔ CARD_NAME:
  서로 비슷한 목적(예: 생활 필수비 위주, 온라인/해외 위주 등)으로 함께 비교·추천되는 카드들

각 관계에 대해 다음 정보를 추출하시오:
- source_entity: 관계의 출발점 엔티티 이름 (1번에서 추출한 entity_name 중 하나)
- target_entity: 관계의 도착점 엔티티 이름 (1번에서 추출한 entity_name 중 하나)
- relationship_description: 이 두 엔티티가 왜, 어떻게 관련되어 있는지에 대한 설명
- relationship_strength: 1~10 사이의 정수. 10에 가까울수록 이 관계가 카드 추천/이해에 매우 중요함을 의미.

각 관계는 다음 형식으로 출력하시오:
("relationship"{tuple_delimiter}<source_entity>{tuple_delimiter}<target_entity>{tuple_delimiter}<relationship_description>{tuple_delimiter}<relationship_strength>)

3. 출력 형식
위에서 정의한 entity와 relationship들을 **하나의 리스트**로 모두 출력하시오.
엔티티와 관계는 **{record_delimiter}** 로 구분하고,
마지막에는 {completion_delimiter} 를 출력하여 응답이 끝났음을 표시하시오.

4. 출력 언어
설명과 관계 설명은 모두 한국어로 작성하시오.

######################
-Examples-
######################
Example 1:

Entity_types: [CARD_NAME, CARD_TYPE, BENEFIT_CATEGORY, SPENDING_CONDITION, FEE_OR_LIMIT, EXCLUSION_RULE]
Text:
"카드의정석2는 국내외 가맹점 1.2% 청구할인을 제공하며, 전월 국내외 가맹점 이용실적 50만원 이상 시 적용됩니다.
분기별 국내외 가맹점 이용실적에 따라 최대 15,000원까지 추가 청구할인을 제공하며,
무이자할부, 세금/공과금, 아파트관리비 등은 할인 및 실적에서 제외됩니다."

Output:
("entity"{tuple_delimiter}"카드의정석2"{tuple_delimiter}"CARD_NAME"{tuple_delimiter}"국내외 가맹점 1.2% 청구할인과 분기별 추가 청구할인을 제공하는 우리카드 상품명"){record_delimiter}
("entity"{tuple_delimiter}"신용카드"{tuple_delimiter}"CARD_TYPE"{tuple_delimiter}"후불 결제 방식으로 이용되는 카드 유형으로, 카드의정석2는 신용카드 상품에 해당함"){record_delimiter}
("entity"{tuple_delimiter}"국내외 가맹점 1.2% 청구할인"{tuple_delimiter}"BENEFIT_CATEGORY"{tuple_delimiter}"모든 국내외 가맹점 이용금액에 대해 1.2% 청구할인을 제공하는 기본 혜택"){record_delimiter}
("entity"{tuple_delimiter}"전월 국내외 가맹점 이용실적 50만원 이상"{tuple_delimiter}"SPENDING_CONDITION"{tuple_delimiter}"기본 1.2% 청구할인을 받기 위해 필요한 최소 전월 실적 요건"){record_delimiter}
("entity"{tuple_delimiter}"분기별 추가 청구할인 최대 15,000원"{tuple_delimiter}"FEE_OR_LIMIT"{tuple_delimiter}"분기별 이용실적 구간에 따라 5,000원~15,000원까지 추가 청구할인을 제공하며, 최대 금액은 15,000원임"){record_delimiter}
("entity"{tuple_delimiter}"무이자할부, 세금/공과금, 아파트관리비 할인 및 실적 제외"{tuple_delimiter}"EXCLUSION_RULE"{tuple_delimiter}"무이자할부, 세금/공과금, 아파트관리비는 할인 및 전월 실적 산정에서 제외됨"){record_delimiter}
("relationship"{tuple_delimiter}"카드의정석2"{tuple_delimiter}"신용카드"{tuple_delimiter}"카드의정석2는 신용카드 유형에 해당하는 카드 상품임"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"카드의정석2"{tuple_delimiter}"국내외 가맹점 1.2% 청구할인"{tuple_delimiter}"카드의정석2의 기본 혜택은 국내외 가맹점 이용금액에 대한 1.2% 청구할인임"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"카드의정석2"{tuple_delimiter}"전월 국내외 가맹점 이용실적 50만원 이상"{tuple_delimiter}"카드의정석2의 기본 1.2% 청구할인은 전월 국내외 가맹점 이용실적이 50만원 이상인 경우에만 제공됨"{tuple_delimiter}9){record_delimiter}
("relationship"{tuple_delimiter}"카드의정석2"{tuple_delimiter}"분기별 추가 청구할인 최대 15,000원"{tuple_delimiter}"카드의정석2는 분기별 이용실적에 따라 최대 15,000원까지 추가 청구할인을 제공함"{tuple_delimiter}8){record_delimiter}
("relationship"{tuple_delimiter}"카드의정석2"{tuple_delimiter}"무이자할부, 세금/공과금, 아파트관리비 할인 및 실적 제외"{tuple_delimiter}"해당 결제 항목들은 카드의정석2에서 할인 및 전월 실적 산정에서 제외되는 예외 항목임"{tuple_delimiter}8){completion_delimiter}

######################
-Real Data-
######################
Entity_types: [{entity_types}]
Text: {input_text}
######################
Output:
"""






PROMPTS[
    "summarize_entity_descriptions"
] = """You are a helpful assistant responsible for generating a comprehensive summary of the data provided below.
Given one or two entities, and a list of descriptions, all related to the same entity or group of entities.
Please concatenate all of these into a single, comprehensive description. Make sure to include information collected from all the descriptions.
If the provided descriptions are contradictory, please resolve the contradictions and provide a single, coherent summary.
Make sure it is written in third person, and include the entity names so we the have full context.

#######
-Data-
Entities: {entity_name}
Description List: {description_list}
#######
Output:
"""


PROMPTS[
    "entiti_continue_extraction"
] = """MANY entities were missed in the last extraction.  Add them below using the same format:
"""

PROMPTS[
    "entiti_if_loop_extraction"
] = """It appears some entities may have still been missed.  Answer YES | NO if there are still entities that need to be added.
"""

PROMPTS["DEFAULT_ENTITY_TYPES"] = [
    "CARD_NAME",                # 카드 상품 자체 (카드의정석2, 우리카드 7CORE 등)
    "CARD_TYPE",                # 신용카드, 체크카드
    "BENEFIT_CATEGORY",    # 편의점, 카페, 배달, 대중교통, 온라인쇼핑, 해외이용 등
    "MERCHANT_OR_BRAND",   # CU, GS25, 스타벅스, 배달의민족, 마스터카드, 국내전용 등
    "SPENDING_CONDITION",  # 전월 실적 50만원 이상, 건당 1만원 이상, 월 3회까지 등
    "FEE_OR_LIMIT",        # 연회비, 월 할인/적립 한도, 분기별 추가할인 구간 등
    "EXCLUSION_RULE"       # 할인 제외 가맹점, 간편결제/PG 결제시 제외, 세금/공과금 등
]

PROMPTS["DEFAULT_TUPLE_DELIMITER"] = "<|>"
PROMPTS["DEFAULT_RECORD_DELIMITER"] = "##"
PROMPTS["DEFAULT_COMPLETION_DELIMITER"] = "<|COMPLETE|>"

PROMPTS["local_rag_response"] = """---Role---

당신은 우리카드 상품(신용/체크카드)의 혜택과 조건을 설명하고,
사용자의 질문에 맞는 카드를 추천해 주는 한국어 카드 상담 어시스턴트입니다.

---Goal---

아래 데이터 테이블(카드 상품 설명, 혜택, 조건, 한도, 제외 항목 등)을 기반으로
사용자의 질문에 답변하십시오.

- 제공된 데이터에 근거하여 설명하고, 근거가 없는 정보는 추측하지 마십시오.
- 필요하다면 일반적인 카드 사용 상식(예: 연회비와 혜택의 트레이드오프)을 간단히 언급할 수 있으나,
  구체적인 수치(할인율, 한도 등)는 반드시 데이터에 있을 때만 사용하십시오.
- 질문이 "카드 추천"에 해당하는 경우,
  가능하면 **추천 카드 TOP3** 형식으로 정리하여 제시하고,
  각 카드별로 간단한 요약/장점/주의사항을 설명하십시오.

---Target response length and format---

{response_type}

응답은 한국어로 작성하고, 마크다운 형식(소제목, 리스트, 표 등)을 적절히 사용하십시오.

---Data tables---

{context_data}

---Detailed Instructions---

1. 사용자의 질문이 어떤 소비 패턴·조건(예: 편의점/카페/배달 위주, 연회비 저렴, 실적 부담 적음 등)을 말하는지 먼저 파악합니다.
2. 데이터 테이블의 내용을 바탕으로, 해당 조건에 잘 맞는 카드/혜택/커뮤니티 정보를 찾아 요약합니다.
3. "카드 추천"이 요구된 경우 아래와 같은 구조를 권장합니다:

### 추천 카드 TOP3
1. 카드명 A
   - 주요 혜택: ...
   - 전월 실적/조건: ...
   - 연회비 및 한도: ...
   - 이런 사람에게 추천: ...
2. 카드명 B
   - ...

4. 단순 조회(특정 카드 혜택만 설명 등)인 경우, 해당 카드에 대한 혜택/조건/예외사항 등을 정리해서 설명합니다.
5. 데이터에 정보가 없거나 불충분할 때는, 솔직하게 "해당 정보는 제공된 데이터에 없음"이라고 말하십시오.

Style the response in markdown.
"""

PROMPTS["global_map_rag_points"] = """---Role---

You are a helpful assistant responding to questions about data in the tables provided.


---Goal---

Generate a response consisting of a list of key points that responds to the user's question, summarizing all relevant information in the input data tables.

You should use the data provided in the data tables below as the primary context for generating the response.
If you don't know the answer or if the input data tables do not contain sufficient information to provide an answer, just say so. Do not make anything up.

Each key point in the response should have the following element:
- Description: A comprehensive description of the point.
- Importance Score: An integer score between 0-100 that indicates how important the point is in answering the user's question. An 'I don't know' type of response should have a score of 0.

The response should be JSON formatted as follows:
{{
    "points": [
        {{"description": "Description of point 1...", "score": score_value}},
        {{"description": "Description of point 2...", "score": score_value}}
    ]
}}

The response shall preserve the original meaning and use of modal verbs such as "shall", "may" or "will".
Do not include information where the supporting evidence for it is not provided.


---Data tables---

{context_data}

---Goal---

Generate a response consisting of a list of key points that responds to the user's question, summarizing all relevant information in the input data tables.

You should use the data provided in the data tables below as the primary context for generating the response.
If you don't know the answer or if the input data tables do not contain sufficient information to provide an answer, just say so. Do not make anything up.

Each key point in the response should have the following element:
- Description: A comprehensive description of the point.
- Importance Score: An integer score between 0-100 that indicates how important the point is in answering the user's question. An 'I don't know' type of response should have a score of 0.

The response shall preserve the original meaning and use of modal verbs such as "shall", "may" or "will".
Do not include information where the supporting evidence for it is not provided.

The response should be JSON formatted as follows:
{{
    "points": [
        {{"description": "Description of point 1", "score": score_value}},
        {{"description": "Description of point 2", "score": score_value}}
    ]
}}
"""





PROMPTS[
    "global_reduce_rag_response"
] = """---Role---

당신은 여러 개의 카드 혜택 커뮤니티 리포트를 종합하여,
사용자의 질문에 담긴 요구사항(소비 패턴·혜택 및 이용 조건 등)에 가장 적합한 카드를 추천하고 각 추천 이유와 혜택·이용 조건을 정리해 주는 우리카드사의 카드 제품 추천 어시스턴트입니다.

---Goal---

여러 분석가(community report 작성자)가 서로 다른 카드 군집을 분석한 리포트를 제공했습니다.
이 리포트들은 이미 "질문과의 관련도"에 따라 **중요도 순(내림차순)**으로 정렬되어 있습니다.

당신의 목표는:
- 이 리포트들을 읽고,
- 사용자 질문에 직접적으로 도움이 되는 정보만 남기고 불필요한 내용은 제거한 뒤,
- "추천 카드 TOP3"와 각 카드의 "추천 이유 / 혜택 요약 / 이용조건 요약"을 한국어로 정리하는 것입니다.

리포트에 카드명이 명시되어 있다면 그대로 사용하고, 리포트에 없는 구체적인 수치(할인율, 한도 등)를 새로 만들어내지는 마십시오.

사용자의 요구사항 정보가 부족하다고 판단되더라도,
가능한 범위에서 TOP3 카드를 구성한 뒤, 마지막에 추가 정보 요청 문장을 한 줄로 덧붙이십시오.

---Target response length and format---

{response_type}

※ 위 {response_type} 값과 관계없이, **응답 형식은 아래 규격만 따라야 합니다.**

---Output Format (VERY STRICT)---

응답 전체는 다음 형식을 정확히 따라야 합니다.
아래에 있는 줄 이외의 문장, 설명, 마크다운 헤더, 불릿 리스트, 공손한 인사말 등을 추가하면 안 됩니다.

반드시 다음 12줄(또는 마지막 안내 문장 포함 시 13줄)만 출력해야 합니다:

1순위 : <카드명 또는 전략명>
추천 이유 : <이 카드가 사용자 요구사항에 잘 맞는 이유를 2~4문장으로 요약>
혜택 요약 : <주요 혜택(카테고리, 할인/적립 구조, 강점)을 2~4문장으로 요약>
이용조건 요약 : <전월 실적, 건당 최소 결제금액, 월/분기 한도, 연회비, 유의해야 할 조건 등을 2~4문장으로 요약>

2순위 : <카드명 또는 전략명>
추천 이유 : <이 카드가 1순위와 비교했을 때 어떤 장단점을 가지는지 2~4문장으로 요약>
혜택 요약 : <주요 혜택을 2~4문장으로 요약>
이용조건 요약 : <전월 실적/연회비/한도 등 핵심 조건을 2~4문장으로 요약>

3순위 : <카드명 또는 전략명>
추천 이유 : <왜 3순위인지, 어떤 상황에서 유리한지 2~4문장으로 요약>
혜택 요약 : <주요 혜택을 2~4문장으로 요약>
이용조건 요약 : <전월 실적/연회비/한도 등 핵심 조건을 2~4문장으로 요약>

(요구사항 정보가 부족하다고 판단되는 경우, 위 12줄 **직후에만** 다음 한 줄을 추가하십시오. 그 외 위치에는 추가하지 마십시오.)
더 정확한 추천을 받기 위해 더 상세하게 받고 싶은 혜택 혹은 필수 충족사항들을 구체적으로 작성해서 보내주세요.

중요 제약:
- 위에 정의된 줄 외의 텍스트(예: "요약", "결론", "추가 설명", 불릿 리스트, 인사말 등)를 절대 출력하지 마십시오.
- 마크다운 헤더(예: "#", "##"), 리스트("- ", "1. ") 등은 사용하지 마십시오.
- 줄 순서와 레이블(1순위 / 추천 이유 / 혜택 요약 / 이용조건 요약 / 2순위 / 3순위)은 그대로 유지해야 합니다.
- 세부 내용이 부족하더라도 형식을 채우되, “리포트에서 확인되지 않음”처럼 솔직히 적을 수 있습니다.
- TOP3는 가급적 서로 다른 카드/전략이 되도록 하십시오.

---Analyst Reports---

{report_data}

---Grounding Rules---

- 리포트에 근거하지 않은 구체적인 수치/조건(할인율 %, 최대 한도 금액 등)을 새로 만들어내지 마십시오.
- 여러 리포트에 같은 정보가 중복되어 있어도, 최종 응답에서는 깔끔하게 합쳐 한 번만 설명하십시오.
- 응답은 사용자의 질문에 직접적으로 도움이 되는 정보 위주로 구성하십시오.
- 사용자 질문에 담긴 요구사항이 추천 결과를 도출하기에 정보가 부족한 경우에도 우선 TOP3를 구성한 뒤,
  마지막 줄에 추가 정보 요청 문장을 반드시 붙이십시오(형식에 명시된 경우에 한함).
"""


PROMPTS[
    "naive_rag_response"
] = """You're a helpful assistant
Below are the knowledge you know:
{content_data}
---
If you don't know the answer or if the provided knowledge do not contain sufficient information to provide an answer, just say so. Do not make anything up.
Generate a response of the target length and format that responds to the user's question, summarizing all information in the input data tables appropriate for the response length and format, and incorporating any relevant general knowledge.
If you don't know the answer, just say so. Do not make anything up.
Do not include information where the supporting evidence for it is not provided.
---Target response length and format---
{response_type}
"""

PROMPTS["fail_response"] = "Sorry, I'm not able to provide an answer to that question."

PROMPTS["process_tickers"] = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

PROMPTS["default_text_separator"] = [
    # Paragraph separators
    "\n\n",
    "\r\n\r\n",
    # Line breaks
    "\n",
    "\r\n",
    # Sentence ending punctuation
    "。",  # Chinese period
    "．",  # Full-width dot
    ".",  # English period
    "！",  # Chinese exclamation mark
    "!",  # English exclamation mark
    "？",  # Chinese question mark
    "?",  # English question mark
    # Whitespace characters
    " ",  # Space
    "\t",  # Tab
    "\u3000",  # Full-width space
    # Special characters
    "\u200b",  # Zero-width space (used in some Asian languages)
]

