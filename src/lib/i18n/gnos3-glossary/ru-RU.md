# Gnos3 business modules — Russian (ru-RU) glossary

## Conventions

- **Form of address: «вы»**, lowercase (as in Russian business software and Open WebUI's catalog), never «ты»: «Выберите компанию», «Это действие нельзя отменить». Impersonal phrasing where it reads naturally («Компаний пока нет», «Не удалось сохранить»).
- **Buttons and menu actions: infinitive**, verb first («Сохранить», «Создать проводку», «Загрузить файл», «Удалить черновик»). Titles and labels: noun phrases («Новая проводка», «Настройки компании»). Status words agree with the noun they describe; for a stand-alone status use the neuter or the noun's gender in context («Проведена» for a проводка, «Сопоставлено» for a line count).
- **Capitalisation**: sentence case — only the first word and proper names capitalised, never English title case («Отчет о прибылях и убытках по периодам»). ALL-CAPS statement totals stay in capitals.
- **Letter ё**: not used (е instead), as Russian business software usually writes: «счет», «отчет», «платеж», «перенесенный».
- **Punctuation**: no space before «:» «?» «!» «;». Quoted UI labels and names in «ёлочки» (inner quotes „…“). Ellipsis «…» for progress («Загрузка…», «Сохранение…»). Dash « — » (em dash with spaces). "e.g." → «например», "i.e." → «т. е.», "etc." → «и т. д.», "incl." → «в т. ч.», "approx." → «около» / «~», "vs." → «против» / «в сравнении с», "No." → «№».
- **Numbers and dates**: decimal comma, (non-breaking) space as thousands separator (1 234,56); dates ДД.ММ.ГГГГ (30.10.2026); months «январь … декабрь» (lowercase; short «янв., февр., март…»); percent «20 %» or as the app formats it. Ranges «янв.–март», «с … по …».
- **Plurals**: Russian has three plural forms, English keys have two. Avoid the problem with a label + colon («Строк: {{count}}», «Выбрано: {{count}}») or a noun that does not change («{{count}} шт.»). Never write «1 строк».
- **Debit / credit** → **дебет / кредит**; column headers **Дт / Кт** for DR / CR.
- **Placeholders** ({{name}}, {name}, <0>…</0>) stay exactly as given; Russian word order may move them, never drop or rename them. A placeholder holding a noun cannot be declined: build the sentence so it stays in the nominative («Налог: {{tax}}», «Декларация ({{tax}})»).
- Product names unchanged: Gnos3, K4mi, SmartOffice, Ollama, Open WebUI, Excel, PDF, CSV, ISO currency codes, units.
- Tax names come from the tax kind, never the country's own label: VAT = «НДС», GST = «GST (налог на товары и услуги)», GST/HST = «GST/HST», sales tax = «налог с продаж», consumption tax = «потребительский налог», ICMS = «ICMS», corporate income tax = «налог на прибыль», Hong Kong profits tax = «налог на прибыль (Profits Tax)», individual income tax = «НДФЛ».
- Settings = «Настройки». Download = «Скачать» (never «Загрузить», which is upload). Dashboard = «Обзор».

## Accounting and finance

| English | Russian (ru-RU) |
|---|---|
| account (ledger; key `Account_gnos3`) | счет (бухгалтерский счет) — never «учетная запись», which is a user account |
| account name / code | наименование счета / код счета |
| account type | тип счета |
| chart of accounts | план счетов |
| chart template | шаблон плана счетов |
| control account (with sub-accounts) | синтетический счет |
| sub-account | субсчет |
| detail / leaf account | аналитический (конечный) счет |
| journal entry / entry / transaction (books) | проводка |
| line (of an entry) | строка проводки |
| journal | журнал |
| general ledger / ledger | главная книга / учет (the books) |
| sub-ledger | вспомогательная книга |
| trial balance | оборотно-сальдовая ведомость (ОСВ) |
| balance sheet | бухгалтерский баланс (short: баланс) |
| profit and loss / income statement / P&L | отчет о прибылях и убытках (ОПУ) |
| statement of financial position (HK) | отчет о финансовом положении |
| statement of profit or loss (HK) | отчет о прибылях и убытках |
| current / non-current assets | оборотные / внеоборотные активы |
| current / non-current liabilities | краткосрочные / долгосрочные обязательства |
| assets / liabilities / equity | активы / обязательства / капитал |
| revenue / income | выручка / доходы |
| expense (account type, P&L) | расходы |
| cost of sales (COGS) | себестоимость продаж |
| retained earnings | нераспределенная прибыль |
| net income / net profit | чистая прибыль |
| opening balance | начальное сальдо (входящий остаток) |
| closing balance (key `Closing_balance`) | конечное сальдо (исходящий остаток) |
| balance (of an account) | сальдо / остаток |
| movement (TB column) | обороты |
| debit / credit (DR / CR) | дебет / кредит (Дт / Кт) |
| draft | черновик |
| post / posted | провести / проведена |
| book (an invoice), booking | отразить в учете, отражение в учете |
| booking defaults | счета по умолчанию |
| void / voided | аннулировать / аннулирована |
| reversal (entry) | сторно (сторнирующая проводка) |
| accounting period | учетный период |
| fiscal year / FY | финансовый год / ФГ |
| year to date (YTD) | с начала года |
| year-end closing | закрытие года |
| close / reopen a period | закрыть / открыть повторно |
| closing checklist | контрольный список закрытия |
| blocker | блокирующая проблема |
| gap (line awaiting an account) | строка без счета |
| bank account | банковский счет |
| bank statement / bank line | банковская выписка / строка выписки |
| bank reconciliation | сверка с банком |
| match / unmatch / matched | сопоставить / отменить сопоставление / сопоставлено |
| match group | группа сопоставления |
| counterparty | контрагент |
| accounts payable / receivable (AP / AR) | кредиторская / дебиторская задолженность |
| AP / AR aging | анализ кредиторской / дебиторской задолженности по срокам |
| vendor / supplier | поставщик |
| customer / client | клиент (покупатель in AR headings) |
| invoice | счет-фактура (pl. счета-фактуры) — keeps it apart from «счет» = ledger account |
| bill (supplier invoice) | счет-фактура поставщика |
| receipt (expense) | чек |
| payment | платеж |
| payment in / out | поступление / списание |
| payer / payee | плательщик / получатель |
| payment method | способ оплаты |
| bank transfer / check / card / cash | банковский перевод / чек / банковская карта / наличные |
| currency / base currency | валюта / базовая валюта |
| exchange rate | курс валюты |
| exchange difference / gain / loss | курсовая разница / положительная / отрицательная курсовая разница |
| exchange clearing account | транзитный счет курсовых разниц |
| categorization rule | правило категоризации |
| bank-line rule | правило для строк выписки |
| pattern (in a rule) | образец |
| template | шаблон |
| split (across accounts) | распределить, распределение |
| fixed asset | основное средство (ОС) |
| depreciation / accumulated depreciation | амортизация / накопленная амортизация |
| useful life / salvage value / book value | срок полезного использования / ликвидационная стоимость / остаточная стоимость |
| expense sheet (employee claim; key `Expenses_tab`) | авансовый отчет |
| reimbursement | возмещение расходов |
| employee | сотрудник |
| approve / reject / submit | утвердить / отклонить / отправить на утверждение |
| VAT / tax | НДС / налог |
| output / input VAT | НДС начисленный / НДС к вычету |
| VAT payable / VAT credit | НДС к уплате / НДС к возмещению |
| credit brought / carried forward | перенесенный остаток к возмещению / остаток к переносу |
| surcharge (China, on VAT) | дополнительный сбор |
| corporate income tax (CIT) | налог на прибыль |
| individual income tax (IIT) | НДФЛ |
| profits tax (Hong Kong) | налог на прибыль (Profits Tax) |
| provisional tax | авансовый платеж по налогу |
| prepaid tax (asset) | предоплаченный налог |
| assessment notice / demand note | налоговое уведомление / требование об уплате |
| tax return / filing | налоговая декларация (декларация) |
| accrual entry (tax) | проводка начисления |
| settlement entry (VAT) | проводка закрытия |
| settle | погасить |
| add-back / deduction | увеличение / уменьшение (налоговой базы) |
| tax computation adjustments | налоговые корректировки |
| assessable profit | налогооблагаемая прибыль |
| losses brought forward | убытки прошлых лет |
| tiered rates | ступенчатые ставки |
| tax role mapping / mapped | привязка налоговых ролей / привязан |
| company | компания |
| legal entity name | полное наименование |
| books language | язык учета |

## Documents and modules

| English | Russian (ru-RU) |
|---|---|
| document | документ |
| tag (K4mi) | метка |
| custom field | пользовательское поле |
| correspondent | корреспондент |
| document type | тип документа |
| workflow | рабочий процесс |
| storage path | путь к хранилищу |
| owner | владелец |
| upload | загрузить, загрузка |
| business card | визитка |
| extraction | извлечение данных |
| confidence | достоверность |
| needs review / mark reviewed | требует проверки / отметить как проверенное |
| reprocess | обработать повторно |
| knowledge base | база знаний |
| anonymise / anonymiser | анонимизировать / Анонимизатор |

## UI words

| English | Russian (ru-RU) |
|---|---|
| settings | настройки |
| dashboard | обзор |
| save / cancel / delete / edit | сохранить / отменить / удалить / редактировать |
| search / filter / sort | поиск / фильтр / сортировка |
| export / import | экспорт / импорт (verbs: экспортировать / импортировать) |
| upload / download | загрузить / скачать |
| apply / confirm / close | применить / подтвердить / закрыть |
| create / add / remove | создать / добавить / удалить |
| loading / saving | загрузка… / сохранение… |
| error / warning | ошибка / предупреждение |
| status / date / amount / total | статус / дата / сумма / итого |
| optional / required | необязательно / обязательно |
| permissions / group / user | разрешения / группа / пользователь |
| admin / superadmin | администратор / суперадминистратор |
