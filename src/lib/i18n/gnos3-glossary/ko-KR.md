# Gnos3 — Korean (ko-KR) glossary

## Conventions

- **Register**: formal polite. Statements, errors and confirmations in 합쇼체 (-습니다 / -ㅂ니다): "저장되었습니다.", "이 작업은 되돌릴 수 없습니다." Instructions and hints in the polite imperative -하세요 (not -십시오): "계정을 선택하세요.", "먼저 회사를 만드세요." Never address the reader as 당신; leave the subject out.
- **Buttons, menu items, tabs, column headers**: nouns or noun phrases, no verb ending, no period: "저장", "취소", "전표 생성", "Excel로 내보내기", "다시 시도". Toggle / checkbox labels may end in -하기 only when a noun reads badly ("검토 완료로 표시").
- **Titles and labels**: noun phrases, no period. Full sentences (help text, messages) end with a period.
- **Spacing (띄어쓰기)**: follow standard Korean spacing. Established compound terms are written as in Korean accounting practice (총계정원장, 계정과목표, 매출원가, 감가상각누계액, 이익잉여금); others keep a space (은행 계좌, 회계 기간, 기준 통화).
- **Particles after placeholders and Latin words**: the value of {{name}} / {name} is unknown, so avoid a particle that depends on the last syllable. Restructure ("{{name}} 삭제됨", "회사: {{name}}") or use the paired form 을(를), 이(가), 은(는), 과(와), (으)로 when there is no way around it.
- **Punctuation**: no space before ":" "?" "!". Quoted UI labels and names in “…” (“{{name}}” 항목이 삭제됩니다). Ellipsis "…". "e.g." = "예:", "i.e." = "즉", "etc." = "등". Use "~" or "–" for ranges as in the source.
- **Numbers and dates**: thousands comma and decimal point (1,234.56), as in Korea. Percent without a space (10%). Dates YYYY-MM-DD or "2026년 3월 31일"; months "1월"…"12월", "2026년 3월".
- **Debit / credit** columns: "차변" / "대변"; DR / CR → 차 / 대.
- **Singular / plural**: Korean has no plural; both forms of a key get the same text ("{count}개 행").
- **Tax placeholders**: UI `{{tax}}` / books `{tax}` is filled with "부가가치세", "GST", "소비세", "판매세"…; put it first or before a noun ("{{tax}} 신고", "{{tax}} 납부액"), never followed by a variable particle. `{{cit}}` is "법인세" / "이윤세".
- **Account (Open WebUI)** = the user's sign-in account ("계정", existing file); **Account_gnos3** = a ledger account ("계정과목"). Inside compounds the short "계정" is used (계정 코드, 계정명, 상대 계정).
- **Product names stay** in Latin script: Gnos3, K4mi, SmartOffice, Ollama, Open WebUI, Excel, PDF, CSV, currency codes, units. Korean particles after them follow pronunciation: Excel로, PDF를, CSV를, K4mi에서.

## Accounting and finance

| English | Korean |
|---|---|
| account (ledger) | 계정 / 계정과목 (standalone `Account_gnos3`) |
| account name / account code | 계정명 / 계정 코드 |
| account type | 계정 유형 |
| chart of accounts | 계정과목표 |
| control account (with sub-accounts) | 통제 계정 |
| sub-account | 하위 계정 |
| detail / leaf account | 세부 계정 |
| journal entry / entry / transaction | 전표 (journal entry in a sentence: 분개) |
| entry line | 전표 행 |
| manual voucher / voucher | 수동 전표 |
| journal | 분개장 |
| general ledger | 총계정원장 |
| sub-ledger | 보조원장 |
| trial balance | 시산표 |
| balance sheet | 재무상태표 |
| income statement / P&L / profit and loss | 손익계산서 |
| statement of financial position (HK) | 재무상태표 |
| statement of profit or loss (HK) | 손익계산서 |
| assets / liabilities / equity | 자산 / 부채 / 자본 |
| current / non-current assets | 유동자산 / 비유동자산 |
| current / non-current liabilities | 유동부채 / 비유동부채 |
| retained earnings | 이익잉여금 |
| revenue / income | 매출 / 수익 |
| cost of sales / COGS | 매출원가 |
| gross profit | 매출총이익 |
| operating profit | 영업이익 |
| net income / profit for the year | 당기순이익 |
| administrative expenses | 관리비 (판매비와관리비) |
| finance costs / financial expenses | 금융비용 |
| expenses (account type, P&L, dashboards) | 비용 |
| opening balance | 기초 잔액 |
| closing balance | 기말 잔액 |
| balance (of an account) | 잔액 |
| debit / credit | 차변 / 대변 |
| draft | 초안 (a draft entry: 초안 전표) |
| post / posted | 전기 / 전기됨 |
| book (an invoice), booking | 기장, 기장 처리 |
| booking defaults | 기본 기장 계정 |
| booking engine | 기장 엔진 |
| gap (line awaiting an account) | 미지정 항목 (계정 미지정 행) |
| void / voided | 무효화 / 무효 ("Void" button = "전표 무효화", never bare "취소" = Cancel) |
| reversal / reverse | 역분개 / 역분개하다 |
| accounting period | 회계 기간 |
| fiscal year / FY | 회계연도 |
| year to date (YTD) | 연간 누계 (누계) |
| year-end closing | 연말 결산 |
| close / reopen (a period) | 마감 / 마감 해제 |
| closing checklist | 결산 점검표 |
| blocker | 차단 항목 |
| bank reconciliation | 은행 대사 |
| match / unmatch / matched | 매칭 / 매칭 해제 / 매칭됨 |
| match group | 매칭 그룹 |
| auto-match | 자동 매칭 |
| bank statement | 은행 거래내역서 |
| bank line | 은행 거래 (one line of a statement) |
| bank account | 은행 계좌 |
| counterparty / counterpart account | 거래 상대방 / 상대 계정 |
| accounts payable (AP) | 매입채무 |
| accounts receivable (AR) | 매출채권 |
| AP / AR aging | 매입채무 / 매출채권 연령 분석 |
| aging bucket / "Current" bucket | 경과 구간 / 만기 전 |
| supplier / vendor | 공급업체 |
| customer / client | 고객 |
| invoice | 인보이스 |
| bill (supplier invoice) / sales invoice | 매입 인보이스 / 매출 인보이스 |
| receipt | 영수증 |
| payment | 결제 (paid out: 지급, received: 수금) |
| payment in / out | 입금 / 출금 |
| payer / payee | 지급인 / 수취인 |
| payment method | 결제 수단 |
| bank transfer / check / credit card / cash | 계좌 이체 / 수표 / 신용카드 / 현금 |
| due date | 만기일 |
| amount | 금액 |
| company | 회사 |
| legal entity name | 법인명 |
| currency / base currency | 통화 / 기준 통화 |
| exchange rate | 환율 |
| exchange difference / gain / loss | 외환차이 / 외환차익 / 외환차손 |
| exchange clearing account | 외환 정산 계정 |
| rate override (company rate) | 회사별 환율 |
| categorization rule | 분류 규칙 |
| bank-line rule | 은행 거래 규칙 |
| pattern | 패턴 |
| split (across accounts) | 분할 |
| template | 템플릿 |
| fixed asset | 고정자산 |
| depreciation / accumulated depreciation | 감가상각 / 감가상각누계액 |
| depreciation charge | 감가상각비 |
| useful life / salvage value / book value | 내용연수 / 잔존가치 / 장부가액 |
| straight-line / declining balance | 정액법 / 정률법 |
| asset register | 고정자산 대장 |
| expense sheet | 경비 정산서 |
| expenses (the expense-claims tab, `Expenses_tab`) | 경비 정산 |
| expense receipt | 증빙 영수증 |
| reimbursement | 경비 환급 |
| employee | 직원 |
| approve / reject / submit | 승인 / 반려 / 제출 |
| VAT | 부가가치세 (short: 부가세) |
| tax (amount / rate on an invoice, generic) | 세금 (세액, 세율, 세금 포함) |
| Tax tab (`Tax_tab`) | 세무 |
| GST / GST/HST / consumption tax / sales tax / ICMS | GST / GST/HST / 소비세 / 판매세 / ICMS |
| output / input VAT | 매출세액 / 매입세액 |
| VAT payable / VAT credit | 납부할 부가세 / 환급 부가세 |
| credit brought forward / carried forward | 전기 이월 공제액 / 차기 이월 공제액 |
| VAT surcharge (China) | 부가 세금 (도시건설유지세, 교육비 부가 등) |
| corporate income tax (CIT) | 법인세 |
| individual income tax (IIT) | 개인소득세 |
| profits tax (Hong Kong) | 이윤세 (Profits Tax) |
| provisional tax | 중간예납세 |
| prepaid tax (asset) | 선납세금 |
| assessment notice / demand note | 과세 통지서 / 납부 고지서 |
| tax return / filing | 세무 신고 (신고) |
| accrual entry (tax) | 계상 전표 |
| settlement entry (VAT) | 정산 전표 |
| settle | 정산 |
| add-back / deduction | 가산 조정 / 차감 조정 |
| tax computation adjustments | 세무 조정 |
| assessable profit | 과세 소득 |
| losses brought forward | 이월결손금 |
| two-tier / tiered rates | 2단계 세율 / 구간별 세율 |
| tax role mapping / mapped | 매핑 / 매핑됨 |
| MPF (HK pension) | MPF (강제적립연금) |

## Documents (K4mi) and modules

| English | Korean |
|---|---|
| document | 문서 |
| tag (K4mi) | 태그 (K4mi 태그) |
| custom field | 사용자 정의 필드 |
| correspondent | 담당자 (as in K4mi's catalog) |
| document type | 문서 유형 |
| storage path | 저장 경로 |
| archive serial number | 보관 일련 번호 |
| inbox | 받은 편지함 |
| owner | 소유자 |
| workflow | 워크플로우 |
| webhook | 웹훅 |
| OCR | OCR |
| extraction / extract | 추출 / 추출하다 |
| reprocess | 재처리 |
| business card | 명함 |
| needs review / mark reviewed | 검토 필요 / 검토 완료로 표시 |
| confidence | 신뢰도 |
| Anonymiser (module and page) / anonymise | 익명화 / 익명화하다 |
| labels mode ([PERSON_1]) / mask / fake values | 레이블 / 마스킹 / 가상 값 |
| decrypt / encrypt | 복호화 / 암호화 |
| knowledge base | 지식 기반 |

## Interface

| English | Korean |
|---|---|
| settings | 설정 |
| dashboard | 대시보드 |
| save | 저장 |
| cancel | 취소 |
| delete | 삭제 |
| edit | 편집 |
| search | 검색 |
| filter | 필터 |
| export / import | 내보내기 / 가져오기 |
| upload / download | 업로드 / 다운로드 |
| apply | 적용 |
| confirm | 확인 |
| close / back | 닫기 / 뒤로 |
| next / previous | 다음 / 이전 |
| create / add / remove | 생성 (만들기) / 추가 / 제거 |
| refresh | 새로 고침 |
| retry | 다시 시도 |
| reset | 초기화 |
| undo | 실행 취소 |
| sync / synced | 동기화 / 동기화됨 |
| key (encryption) | 키 |
| preview | 미리보기 |
| details | 세부 정보 |
| loading… | 로딩 중… |
| error / warning | 오류 / 경고 |
| required / optional | 필수 / 선택 사항 |
| user / group / permission / role | 사용자 / 그룹 / 권한 / 역할 |
| admin / superadmin | 관리자 / 최고 관리자 |
| status | 상태 |
| all / none | 전체 / 없음 |
