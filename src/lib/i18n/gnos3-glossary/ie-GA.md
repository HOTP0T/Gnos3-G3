# Gnos3 business modules — Irish (Gaeilge, ie-GA) glossary

Gnos3 codes the language ie-GA; K4mi calls it ga-IE. Terminology follows téarma.ie (the National Terminology Database) and the Irish forms the Revenue Commissioners (na Coimisinéirí Ioncaim) use; UI words follow Gnos3's existing `ie-GA/translation.json` (Open WebUI). K4mi has no Irish targets yet, so its document words are set here.

## Conventions

- **Form of address: "tú"** (singular), as Irish software and the app's existing file do: "An bhfuil tú cinnte gur mian leat … a scriosadh?". Prefer the autonomous (impersonal) verb for results and errors: "Sábháladh an iontráil", "Níorbh fhéidir an comhad a uaslódáil", "Scriosadh go rathúil".
- **Buttons and menu items: imperative singular**, as in translation.json: "Sábháil", "Cealaigh", "Scrios", "Cuir in eagar", "Cruthaigh iontráil", "Easpórtáil go Excel". Tabs, titles and column headers are nouns ("Iontrálacha", "Íocaíochtaí", "Socruithe").
- **Sentence case** for titles, tabs and buttons ("Clár comhardaithe", not "Clár Comhardaithe"). Proper nouns, languages and nationalities keep their capital (Béarla, Fraincis, Hong Cong). Statement totals written in capitals in English stay in capitals.
- **Mutations**: write the grammar the noun needs (an cuntas / an chuideachta / na cuideachta / an t-airgeadra / ar an mbanc). Before a placeholder whose word is unknown ({{name}}, {{tax}}, {code}) do not mutate or decline it: "cuntas {{code}}", "sonrasc {{number}}", "an tuairisceán {{tax}}" — put a fixed noun in front of the placeholder instead of an article.
- **Punctuation**: no space before ":" "?" "!"; quotes “ ” around quoted labels and values (“{{name}}”); ellipsis "…" ("Ag lódáil…", "Ag sábháil…"); "m.sh." for "e.g."; "srl." for "etc.".
- **Numbers and dates**: Ireland uses the decimal point and the comma for thousands (1,234.56; the app formats numbers itself); dates dd/mm/bbbb; 24-hour clock; months and weekdays take a capital (Eanáir, an Luan).
- **Abbreviations**: D / C for debit / credit (DR / CR: dochar / creidmheas); BA for fiscal year (FY: bliain airgeadais); BGD for year to date (YTD: bliain go dáta); CBL for VAT; IS for AI (intleacht shaorga); B&C for P&L where space is short.
- **Product and data names stay**: Gnos3, K4mi, SmartOffice, Ollama, Open WebUI, Excel, PDF, CSV, JSON, currency codes, MPF, IRD, IBAN, account codes, references (VAT-2026-09, CLOSE-…).

## Bookkeeping

| English | Irish | Notes |
|---|---|---|
| account (ledger) | cuntas (pl. cuntais) | `Account_gnos3`; a user account is also "cuntas" in Open WebUI |
| account name | ainm an chuntais | |
| account code | cód cuntais | |
| chart of accounts | cairt chuntas | |
| sub-account | fochuntas | |
| detail (leaf) account | cuntas mionsonraí (bunleibhéal) | |
| control account | cuntas rialaithe | an account with sub-accounts |
| parent account | máthairchuntas | |
| journal entry / entry / transaction (journal) | iontráil dialainne / iontráil (pl. iontrálacha) | "Transaction" in the ledger UI is always an entry |
| line (of an entry) | líne (pl. línte) | |
| journal | dialann | |
| general ledger / ledger | mórleabhar ginearálta / mórleabhar | |
| sub-ledger | fo-mhórleabhar | |
| trial balance | triailchothromaíocht | |
| balance sheet | clár comhardaithe | |
| profit and loss / P&L / income statement | brabús agus caillteanas (B&C) / ráiteas ioncaim | |
| statement of financial position (HK) | ráiteas ar an staid airgeadais | |
| statement of profit or loss (HK) | ráiteas brabúis nó caillteanais | |
| assets / liabilities / equity | sócmhainní / dliteanais / cothromas | |
| current / non-current assets | sócmhainní reatha / neamhreatha | same for liabilities (dliteanais reatha) |
| revenue / income | ioncam | |
| expenses (account type, P&L) | costais | |
| cost of sales | costas díolacháin | |
| gross / net profit | ollbhrabús / glanbhrabús | |
| retained earnings | tuilleamh coimeádta | |
| balance | iarmhéid | |
| opening / closing balance | iarmhéid tosaigh / iarmhéid deiridh | |
| debit / credit | dochar / creidmheas (D / C) | |
| draft | dréacht | |
| post / posted | postáil / postáilte | "Postáil an iontráil" |
| book (an invoice), booking | cuir de chuntas / cur de chuntas | booking defaults = réamhshocruithe cur de chuntas |
| void / voided | neamhnigh / neamhnithe | never "Cealaigh" (= Cancel) |
| reversal entry | iontráil aisiompaithe | |
| accounting period / period | tréimhse chuntasaíochta / tréimhse | |
| fiscal year | bliain airgeadais (BA) | |
| year to date | bliain go dáta (BGD) | |
| year-end closing | dúnadh deireadh bliana | |
| close / reopen (a period) | dún / athoscail | |
| closing checklist | seicliosta dúnta | |
| blocker | bacainn | |
| gap (line awaiting an account) | bearna | "line awaiting an account" = líne ag fanacht le cuntas |
| template | teimpléad | |

## Banking, payments, currencies

| English | Irish | Notes |
|---|---|---|
| bank reconciliation | réiteach bainc | |
| match / unmatch / matched | meaitseáil / dímheaitseáil / meaitseáilte | |
| match group | grúpa meaitseála | |
| bank statement | ráiteas bainc | |
| bank line / statement line | líne bhainc / líne ráitis | |
| bank account | cuntas bainc | |
| payment | íocaíocht | |
| payment in / out | íocaíocht isteach / amach | |
| payer / payee | íocóir / íocaí | |
| payment method | modh íocaíochta | |
| bank transfer / cheque / credit card / cash | aistriú bainc / seic / cárta creidmheasa / airgead tirim | |
| counterparty | contrapháirtí | |
| supplier / vendor | soláthraí | |
| customer | custaiméir | |
| accounts payable / receivable | cuntais iníoctha / cuntais infhála | |
| AP / AR aging | aosú na gcuntas iníoctha / infhála | |
| currency / base currency | airgeadra / bunairgeadra | |
| exchange rate | ráta malairte | |
| exchange difference / gain / loss | difríocht mhalairte / gnóthachan malairte / caillteanas malairte | |
| exchange clearing account | cuntas imréitigh malairte | |
| categorization rule | riail chatagóiriúcháin | |
| pattern | patrún | |
| split (across accounts) | roinn / roinnt | |
| fixed asset | sócmhainn sheasta | |
| depreciation / accumulated depreciation | dímheas / dímheas carntha | |
| book value / useful life / salvage value | glanluach de réir na leabhar / saolré úsáideach / luach fuílligh | |

## Invoices, expenses, taxes

| English | Irish | Notes |
|---|---|---|
| invoice | sonrasc (pl. sonraisc) | |
| bill (supplier invoice) | bille soláthraí | |
| receipt | admháil | |
| expense | costas | |
| expense sheet / expense claim | bileog chostas / éileamh ar chostais | `Expenses_tab` = Éilimh ar chostais (the claims tab); Expenses in the P&L = Costais |
| trip (expense app) | turas | submit / recall a trip = cuir isteach / aisghair turas |
| reimbursement | aisíocaíocht | |
| employee | fostaí | |
| approve / reject / submit | faomh / diúltaigh / cuir isteach | |
| tax | cáin (gen. cánach) | |
| VAT / GST / sales tax / consumption tax | CBL (cáin bhreisluacha) / CES (cáin ar earraí agus seirbhísí) / cáin díolacháin / cáin tomhaltais | |
| output / input VAT | CBL aschuir / CBL ionchuir | |
| VAT payable / VAT credit | CBL iníoctha / creidmheas CBL | |
| corporate income tax | cáin chorparáide | |
| individual income tax | cáin ioncaim phearsanta | |
| profits tax (Hong Kong) | cáin bhrabús | |
| provisional tax / prepaid tax | cáin shealadach / cáin réamhíoctha | |
| tax return / filing | tuairisceán cánach / comhdú | |
| assessment notice / demand note | fógra measúnachta / nóta éilimh | |
| accrual / accrual entry | fabhrú / iontráil fabhraithe | |
| settle / settlement entry | socraigh / iontráil socraíochta | |
| add-back / deduction (tax computation) | suim curtha leis / asbhaint | |
| tax adjustments | coigeartuithe cánach | |
| assessable profit | brabús inmheasúnaithe | |
| losses brought forward | caillteanais a tugadh ar aghaidh | |
| company | cuideachta | |
| legal name | ainm dlíthiúil | |
| country | tír | |
| business card | cárta gnó | |
| needs review | le hathbhreithniú | |
| extraction | asbhaint | |
| confidence | muinín | |
| reprocess | athphróiseáil | |
| anonymise / anonymiser | anaithnidigh / Anaithniditheoir | |
| pseudonymise | cuir ainm bréige ar | |

## Documents (K4mi)

| English | Irish |
|---|---|
| document | doiciméad (pl. doiciméid) |
| tag | clib (pl. clibeanna) |
| custom field | réimse saincheaptha |
| correspondent | comhfhreagraí |
| document type | cineál doiciméid |
| storage path | conair stórála |
| workflow | sreabhadh oibre |
| upload | uaslódáil |
| owner | úinéir |
| archive serial number | sraithuimhir chartlainne |
| inbox | bosca isteach |
| saved view | amharc sábháilte |
| trash | bruscar |

## Interface words (from the app's existing ie-GA file)

| English | Irish |
|---|---|
| settings | Socruithe |
| dashboard | deais |
| save / cancel / delete / remove | Sábháil / Cealaigh / Scrios / Bain |
| edit / create / add | Cuir in eagar / Cruthaigh / Cuir leis |
| search / filter | Cuardaigh / Scagaire (verb: scag) |
| sort by | Sórtáil de réir |
| export / import | Easpórtáil / Iompórtáil |
| upload / download | Uaslódáil / Íoslódáil |
| apply / confirm | Cuir i bhfeidhm / Deimhnigh |
| close / back / next / previous | Dún / Ar ais / Ar aghaidh / Siar |
| loading / saving | Ag lódáil… / Ag sábháil… |
| error / warning | earráid / rabhadh |
| retry / refresh / reset / clear | Bain triail eile as / Athnuaigh / Athshocraigh / Glan |
| status / date / amount / total | stádas / dáta / méid / iomlán |
| open / view / details | Oscail / Féach / Sonraí |
| enabled / disabled | cumasaithe / díchumasaithe |
| required / optional | riachtanach / roghnach |
| permissions / group / role | ceadanna / grúpa / ról |
| user / admin | úsáideoir / riarthóir |
