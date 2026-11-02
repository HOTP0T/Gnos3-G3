# Gnos3 — Српски (ћирилица) glossary (sr-RS)

## Conventions

- **Script and standard**: Serbian, **Cyrillic**, ekavian (вредност, примени, месец, извештај, успех) for Gnos3, Finances, module messages, Open WebUI and the expense app. **K4mi is the exception**: its catalog (sr-CS) is **Latin** — for K4mi strings write the same terms in Latin (dokument, oznaka, korespondent, tip dokumenta, prilagođeno polje, proces, kontrolna tabla, otpremi).
- **Serbian (not Croatian / Bosnian) word choice**: предузеће, курс (exchange rate), колона, табела, тачка / тачно, прималац / платилац, лични, шаблон, услов, финансијски, недеља (week), хиљада, датотека, рачунар, подешавања.
- **Form of address**: polite plural "ви", lowercase in running UI text, as the existing Open WebUI catalog does ("Унесите назив", "Да ли сигурно желите…", "Изаберите предузеће"). Never "ти" in sentences.
- **Buttons and menu items**: short imperative, 2nd person singular, as the existing catalog does (Сачувај, Откажи, Обриши, Измени, Додај, Направи, Потврди, Примени, Прокњижи, Сторнирај, Упари). Column headers and labels are nouns (Датум, Износ, Конто, Опис).
- **Case**: sentence case — only the first word and proper names capitalised (Главна књига, Бруто биланс, not "Главна Књига"). Month and weekday names are lowercase (јануар, понедељак). ALL-CAPS statement totals stay in capitals.
- **Punctuation**: no space before ":" "?" "!"; quotation marks „…“ around quoted UI labels and names; "нпр." for "e.g.", "тј." for "i.e.", "итд." for "etc."; keep the source's ellipsis ("…" or "...").
- **Numbers and dates**: decimal comma, dot as thousands separator (1.234,56); dates dd.mm.yyyy. (31.12.2026.); currency after the amount (1.234,56 RSD). Formatting itself is done in code — only write numbers in prose this way.
- **Months**: јануар, фебруар, март, април, мај, јун, јул, август, септембар, октобар, новембар, децембар.
- **DR / CR**: Дуг. / Потр. (дугује / потражује).
- **Acronyms and product names** stay in Latin: Gnos3, K4mi, SmartOffice, Ollama, Open WebUI, Excel, PDF, CSV, API, URL, JSON, AI, OCR, IBAN, currency codes, units. Serbian tax acronyms are Cyrillic: ПДВ.
- **Grammar with placeholders**: Serbian nouns change with the number; when a `{{count}}` / `{count}` precedes a noun, prefer a form that reads for any number ("Ставки: {{count}}", "Број ставки: {{count}}") over a wrong plural.
- **Tax names in placeholders** (`{{tax}}` / `{tax}` = ПДВ, GST…): put the name where its case does not matter ("Пријава — {{tax}}", "{{tax}}: обавеза", "обавеза за {{tax}}"), since acronyms stay undeclined.

## Terms

| English | Српски |
|---|---|
| account (ledger) | конто |
| accounts (ledger) | конта |
| account code / account name | шифра конта / назив конта |
| account type | врста конта |
| chart of accounts | контни план |
| control account (has sub-accounts) | синтетички конто |
| sub-account | подконто |
| detail / leaf account | аналитички конто |
| journal entry / entry / transaction | књижење (pl. књижења) |
| entry line | ставка књижења |
| journal | дневник |
| general ledger | главна књига |
| sub-ledger | помоћна књига |
| trial balance | бруто биланс |
| balance sheet | биланс стања |
| profit and loss / income statement | биланс успеха |
| statement of financial position (HK) | извештај о финансијској позицији |
| statement of profit or loss (HK) | извештај о добитку или губитку |
| current / non-current assets | обртна / стална имовина |
| current / non-current liabilities | краткорочне / дугорочне обавезе |
| assets / liabilities / equity | имовина / обавезе / капитал |
| revenue / income | приходи |
| expenses (account type, P&L) | расходи |
| expenses (expense-claims tab, `Expenses_tab`) | обрачуни трошкова |
| cost of sales | трошкови продатог (набавна вредност продате робе) |
| retained earnings | нераспоређени добитак |
| opening balance | почетно стање |
| closing balance | завршно стање |
| balance (of an account) | салдо |
| debit / credit | дугује / потражује (Дуг. / Потр.) |
| draft | нацрт |
| post / posted | прокњижи / прокњижено |
| book (an invoice) / booking | књижи / књижење |
| booking defaults | подразумевана књижења |
| void / voided | сторнирај / сторнирано |
| reversal (entry) | сторно књижење |
| accounting period / period | обрачунски период / период |
| fiscal year (FY) | пословна година (ПГ) |
| year to date (YTD) | од почетка године (кумулативно) |
| year-end closing | годишње закључење |
| close / reopen (a period) | закључи / поново отвори |
| closing checklist | контролна листа закључења |
| blocker | препрека |
| gap (line awaiting an account) | ставка на чекању |
| bank reconciliation | усаглашавање са изводом |
| reconcile / reconciled | усагласи / усаглашено |
| match / unmatch / matched | упари / поништи упаривање / упарено |
| match group | група упаривања |
| bank statement | извод (банковни извод) |
| bank line (statement line) | ставка извода |
| bank account | банковни рачун |
| counterparty | партнер |
| counterparty account (AP/AR) | конто партнера |
| accounts payable / receivable | обавезе према добављачима / потраживања од купаца |
| AP / AR aging | старосна структура обавеза / потраживања |
| "Current" aging bucket | недоспело |
| supplier / vendor | добављач |
| customer / client | купац |
| invoice | фактура |
| bill (supplier invoice) / sales invoice | улазна фактура / излазна фактура |
| receipt (proof of an expense) | рачун (доказ о трошку) |
| payment | плаћање |
| payment in / out | уплата / исплата |
| payer / payee | платилац / прималац |
| payment method | начин плаћања |
| bank transfer / cheque / card / cash | банковни пренос / чек / картица / готовина |
| due date | датум доспећа |
| currency / base currency | валута / основна валута |
| exchange rate | курс |
| exchange difference / gain / loss | курсна разлика / позитивна курсна разлика / негативна курсна разлика |
| exchange clearing account | прелазни конто за конверзију |
| rate override (company) | посебан курс |
| categorization rule | правило категоризације |
| bank-line rule | правило за ставке извода |
| pattern | образац |
| split (across accounts) | расподели / расподела |
| fixed asset | основно средство |
| depreciation / accumulated depreciation | амортизација / акумулирана амортизација |
| useful life / salvage value / book value | корисни век / резидуална вредност / књиговодствена вредност |
| expense sheet | обрачун трошкова |
| reimbursement | рефундација |
| employee | запослени |
| approve / reject / submit | одобри / одбиј / поднеси |
| VAT | ПДВ (порез на додату вредност) |
| output VAT / input VAT | излазни ПДВ / улазни ПДВ (претходни порез) |
| VAT payable / VAT credit | обавеза за ПДВ / ПДВ претплата |
| credit brought / carried forward | пренета претплата / претплата за пренос |
| GST / sales tax / consumption tax | GST (порез на робу и услуге) / порез на промет / порез на потрошњу |
| surcharge (on VAT, China) | прирез |
| corporate income tax (CIT) | порез на добит |
| profits tax (Hong Kong) | порез на добит (Хонгконг) |
| individual income tax (IIT) | порез на доходак |
| provisional tax | аконтација пореза |
| prepaid tax | унапред плаћени порез |
| assessment notice / demand note | пореско решење / позив за плаћање аконтације |
| tax return / filing | пореска пријава / пријава |
| accrual entry (tax) | књижење обрачуна |
| settlement entry (VAT) | књижење измирења |
| settle | измири |
| add-back / deduction | увећање / умањење (пореске основице) |
| tax adjustments | пореске корекције |
| assessable profit | опорезива добит |
| losses brought forward | пренети губици |
| tiered rates | стопе по разредима |
| tax role mapping / mapped | повезивање / повезано |
| template | шаблон |
| company | предузеће |
| legal entity name | пословно име |
| business card | визит карта |
| needs review / mark reviewed | за проверу / означи као проверено |
| confidence (extraction) | поузданост |
| document | документ |
| tag | ознака |
| custom field | прилагођено поље |
| correspondent | кореспондент |
| document type | тип документа |
| storage path | путања складишта |
| workflow | процес |
| upload | отпреми (noun: отпремање) |
| download | преузми (noun: преузимање) |
| file | датотека |
| settings | подешавања |
| dashboard | контролна табла |
| save | сачувај |
| cancel | откажи |
| delete / remove | обриши / уклони |
| edit | измени |
| create / add | направи / додај |
| search | претражи (noun: претрага) |
| filter | филтер (verb: филтрирај) |
| export / import | извези / увези (nouns: извоз / увоз) |
| apply | примени |
| confirm | потврди |
| refresh | освежи |
| loading… | учитавање… |
| error / warning | грешка / упозорење |
| status | статус |
| date / amount / total | датум / износ / укупно |
| reference | референца |
| preview / details | преглед / детаљи |
| user / group / permissions | корисник / група / дозволе |
| admin | администратор |
| anonymise / anonymiser | анонимизуј / анонимизатор (product label "Anonymiser" → Анонимизатор) |
