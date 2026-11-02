# Gnos3 business modules — Bulgarian (bg-BG) glossary

## Conventions

- **Register**: formal, polite plural ("Изберете", "Въведете", "Проверете"). Pronouns of address in lower case, as the Open WebUI Bulgarian file does ("вашата фирма", "ви"); leave them out wherever the verb already says who acts.
- **Buttons and menu commands**: verbal nouns, as K4mi's Bulgarian catalog does: "Запазване", "Изтриване", "Създаване на статия", "Осчетоводяване", "Анулиране". Cancel = "Отказ"; OK = "OK"; Close = "Затваряне".
- **Case**: sentence case for labels, titles and buttons. ALL-CAPS statement totals stay in capitals (АКТИВИ, ОБЩО ПАСИВИ).
- **Punctuation**: no space before ":" "?" "!" ";"; Bulgarian quotation marks „…“ around quoted UI labels and names; spaced em dash " — "; single-character ellipsis "…"; "напр." for e.g., "т.е." for i.e., "→" kept in menu paths (Настройки → Държави).
- **Numbers and dates** are formatted by the code (decimal comma, space as thousands separator, DD.MM.YYYY); in text write "г." after a year only when it stands alone in a sentence ("през 2026 г.").
- **Debit / credit** abbreviations: Д / К (DR → Д, CR → К).
- **Agreement**: "статия" and "фактура" are feminine, so entry / invoice statuses are feminine (осчетоводена, анулирана, съпоставена); "плащане" is neuter (осчетоводено); "ред" is masculine (съпоставен). A `{{tax}}` / `{tax}` placeholder may be ДДС, GST, данък върху продажбите…: write "декларация за {{tax}}", "сметки за {{tax}}" so the sentence reads for any of them.
- **Product names** stay as they are: Gnos3, K4mi, SmartOffice, Finances, Ollama, Open WebUI, Excel, PDF, CSV; currency codes and units unchanged. Statutory form names (IR56B, MPF, HKFRS, SME-FRS, CAS, PCG) stay as codes.
- **Keys with a context suffix** (`Account_gnos3`, `Tax_tab`, `Expenses_tab`): translate the word in that sense only.

## Terms

| English | Bulgarian |
|---|---|
| account (ledger) | сметка |
| account (user login) | акаунт |
| account code / account name | код на сметката / наименование на сметката |
| chart of accounts | сметкоплан |
| chart template | шаблон на сметкоплан |
| control account (with sub-accounts) | синтетична сметка |
| sub-account | подсметка |
| detail / leaf account | аналитична (крайна) сметка |
| account type | вид сметка |
| journal entry / entry / transaction (in the books) | счетоводна статия / статия |
| entry line | ред на статията |
| journal | дневник |
| general ledger | главна книга |
| sub-ledger | спомагателна книга |
| trial balance | оборотна ведомост |
| balance sheet | счетоводен баланс / баланс |
| profit and loss / income statement | отчет за приходите и разходите |
| statement of financial position (HK) | отчет за финансовото състояние |
| statement of profit or loss (HK) | отчет за печалбата или загубата |
| assets / liabilities / equity | активи / пасиви (задължения) / собствен капитал |
| current / non-current assets | текущи / нетекущи активи |
| current / non-current liabilities | текущи / нетекущи пасиви |
| retained earnings | неразпределена печалба |
| revenue / income | приходи |
| expenses (account type, P&L, dashboards) | разходи |
| expenses (the expense-claims tab, key `Expenses_tab`) | разходни отчети |
| cost of sales | себестойност на продажбите |
| gross profit / operating profit / net income | брутна печалба / оперативна печалба / нетна печалба |
| opening balance | начално салдо |
| closing balance | крайно салдо |
| balance (of an account) | салдо |
| movement (TB column) | обороти |
| debit / credit | дебит / кредит (Д / К) |
| draft | чернова |
| post / posted | осчетоводяване / осчетоводена |
| void / voided | анулиране / анулирана |
| reversal (entry) | сторниране / сторнираща статия |
| book (an invoice) / booking | осчетоводяване / осчетоводяване |
| booking defaults | сметки по подразбиране за осчетоводяване |
| booking engine | механизъм за осчетоводяване |
| gap (line awaiting an account) | ред без сметка |
| incomplete (entry with gaps) | непълна |
| accounting period | счетоводен период |
| fiscal year / FY | финансова година / ФГ |
| year to date (YTD) | от началото на годината (натрупано) |
| year-end closing | годишно приключване |
| close / reopen a period | приключване / повторно отваряне |
| closing checklist | проверки преди приключване |
| blocker | блокиращ проблем |
| bank reconciliation | банково равнение |
| match / unmatch / matched | съпоставяне / отмяна на съпоставянето / съпоставен(а) |
| unmatched | несъпоставен(а) |
| match group | група за съпоставяне |
| auto-match | автоматично съпоставяне |
| bank statement | банково извлечение |
| bank line / statement line | ред от извлечение |
| bank account | банкова сметка |
| counterparty | контрагент |
| accounts payable / receivable | задължения към доставчици / вземания от клиенти |
| AP / AR aging | възрастов анализ на задълженията / на вземанията |
| supplier / vendor | доставчик |
| customer / client | клиент |
| invoice | фактура |
| bill (supplier invoice) | фактура от доставчик |
| credit note | кредитно известие |
| receipt (till / expense receipt) | касова бележка / разходен документ |
| payment | плащане |
| payment in / out | постъпление / плащане (входящо / изходящо плащане) |
| payer / payee | платец / получател |
| payment method | начин на плащане |
| bank transfer / check / card / cash | банков превод / чек / карта / в брой |
| currency / base currency | валута / базова валута |
| exchange rate | валутен курс |
| exchange difference / gain / loss | курсова разлика / положителна / отрицателна курсова разлика |
| exchange clearing account | транзитна сметка за валутни операции |
| rate override (per company) | специфичен курс |
| categorization rule | правило за категоризиране |
| bank-line rule | правило за редове от извлечение |
| pattern (in a rule) | образец |
| template | шаблон |
| split (across accounts) | разпределяне / разпределение |
| fixed asset | дълготраен актив |
| depreciation / accumulated depreciation | амортизация / натрупана амортизация |
| useful life / salvage value / book value | полезен живот / остатъчна стойност / балансова стойност |
| straight-line / declining balance | линеен / намаляващ остатък |
| asset register | регистър на дълготрайните активи |
| expense sheet / reimbursement sheet | разходен отчет |
| expense category | категория разход |
| reimbursement | възстановяване на разходи |
| employee | служител |
| approve / reject / submit | одобряване / отхвърляне / подаване |
| company | фирма |
| legal name | фирмено наименование |
| business unit | бизнес звено |
| VAT | ДДС |
| GST / GST-HST / sales tax / consumption tax | GST / GST-HST / данък върху продажбите / потребителски данък |
| output / input VAT | ДДС по продажби / ДДС по покупки |
| VAT payable / VAT credit | ДДС за внасяне / ДДС за възстановяване |
| credit brought forward / carried forward | пренесен кредит от предходен период / кредит за пренасяне |
| surcharge (China) | допълнителна такса |
| corporate income tax (CIT) | корпоративен данък |
| individual income tax (IIT) | данък върху доходите на физическите лица (ДДФЛ) |
| profits tax (Hong Kong) | данък върху печалбата |
| provisional tax | авансов данък |
| prepaid tax (asset) | предплатен данък |
| assessment notice / demand note | известие за оценка / известие за плащане |
| tax return / filing | данъчна декларация / декларация |
| accrual entry | статия за начисляване |
| settlement entry (VAT) | статия за приключване |
| settle (a filing) | уреждане |
| add-back / deduction | увеличение / намаление |
| tax computation adjustments | данъчни преобразувания |
| assessable / adjusted profit | облагаема печалба / данъчна печалба |
| losses brought forward | пренесени данъчни загуби |
| two-tier / tiered rates | двустепенни ставки / ставки по прагове |
| tax rate | данъчна ставка |
| due date | падеж / срок за плащане |
| mapping / mapped (tax role → account) | обвързване / обвързана |
| business card | визитна картичка |
| needs review / mark reviewed | за проверка / маркиране като проверена |
| extraction / confidence | извличане / увереност |
| reprocess | повторна обработка |
| anonymise / anonymiser | анонимизиране / Анонимизатор |
| pseudonymise / decrypt | псевдонимизиране / декриптиране |
| document | документ |
| tag (K4mi) | етикет |
| custom field | персонализирано поле |
| correspondent | кореспондент |
| document type | тип документ |
| storage path | път за съхранение |
| workflow | работен процес |
| owner | собственик |
| knowledge base / data source | база от знания / източник на данни |
| permissions / group | разрешения / група |
| settings | Настройки |
| dashboard | табло |
| save | Запазване |
| cancel | Отказ |
| delete | Изтриване |
| edit | Редактиране |
| add / create | Добавяне / Създаване |
| search / filter | Търсене / Филтриране |
| export / import | Експортиране / Импортиране |
| upload / download | Качване / Изтегляне |
| apply / confirm | Прилагане / Потвърждаване |
| refresh / reset / clear | Опресняване / Нулиране / Изчистване |
| preview / details | Преглед / Подробности |
| loading… | Зареждане… |
| error / warning | Грешка / Предупреждение |
| status | състояние |
| amount / total | сума / общо |
| reference (entry ref) | референция |
