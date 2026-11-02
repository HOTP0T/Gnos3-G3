# Gnos3 business modules — Czech (cs-CZ) glossary

## Conventions

- **Register**: formal "vy" (vykání), lowercase in running text ("Vyberte účet", "Zadejte kurz"). Never tykání.
- **Buttons and menu items**: infinitive ("Uložit", "Vytvořit zápis", "Zaúčtovat", "Stornovat zápis"). Instructions in messages: polite imperative plural ("Vyberte…", "Zkontrolujte…").
- **Case**: sentence case — only the first word and proper names capitalised ("Výchozí zaúčtování", not "Výchozí Zaúčtování"). ALL-CAPS statement totals stay in capitals.
- **Punctuation**: no space before ":" "?" "!"; Czech quotes „…" for quoted UI labels and names; spaced en dash " – " for asides and ranges in prose; "…" (one character) for "loading…"; "např." for "e.g.", "tj." for "i.e.", "atd." for "etc."; arrows "→" in paths stay ("Nastavení → Kurzy").
- **Numbers and dates**: decimal comma, space (non-breaking) as thousands separator (1 234,56); date d. M. yyyy (30. 10. 2026); percentages with a space ("15 %"). Currency codes (CZK, EUR, USD, HKD) and units stay as they are.
- **MD / D**: debit = má dáti (MD), credit = dal (D). Column headers "MD" / "D"; DR / CR in source → MD / D.
- **Placeholders**: Czech declines nouns; build sentences so a `{{name}}` / `{name}` stays in the nominative — apposition after a noun ("účet {{code}}", "společnost „{{name}}"") or after a colon ("Chybí účet: {{code}}").
- **Counts**: Czech has three plural forms (1 / 2–4 / 5+). When the source has a bare `{{count}} rows`, prefer a neutral form "Řádky: {{count}}" / "Počet řádků: {{count}}"; when a key is explicitly singular ("1 row") or plural, use the matching form, with 5+ (genitive plural) as the default plural.
- **Tax names** inserted as `{{tax}}` / `{tax}`: treat as feminine ("DPH", "daň") — "{{tax}} na výstupu", "přiznání k {{tax}}" is avoided; prefer "přiznání ({{tax}})" or "{{tax}}: přiznání".
- **Product names** stay: Gnos3, K4mi, SmartOffice, Ollama, Open WebUI, Excel, PDF, CSV.
- **Delete vs Remove**: Delete = Smazat (destroys data), Remove = Odebrat (takes out of a list / unassigns). Void = Stornovat (never "Zrušit", which is Cancel).

## Terms

| English | Czech |
|---|---|
| account (ledger) | účet |
| account name | název účtu |
| account code | číslo účtu (kód účtu) |
| chart of accounts | účtový rozvrh |
| control account (with sub-accounts) | syntetický účet |
| sub-account | podúčet (analytický účet) |
| detail / leaf account | koncový účet |
| account type | typ účtu |
| assets / liabilities / equity | aktiva / závazky / vlastní kapitál |
| revenue / income | výnosy |
| expenses (account type, P&L, dashboards) | náklady |
| expenses (expense-claims tab, key `Expenses_tab`) | výdaje zaměstnanců |
| journal entry / entry / transaction | účetní zápis / zápis |
| journal | účetní deník |
| voucher (manual entry document) | účetní doklad |
| general ledger | hlavní kniha |
| sub-ledger | pomocná kniha |
| trial balance | obratová předvaha |
| balance sheet | rozvaha |
| income statement / P&L / profit & loss | výkaz zisku a ztráty |
| statement of financial position (HK) | výkaz o finanční pozici |
| statement of profit or loss (HK) | výkaz zisku nebo ztráty |
| current / non-current assets | oběžná / dlouhodobá aktiva |
| current / non-current liabilities | krátkodobé / dlouhodobé závazky |
| retained earnings | nerozdělený zisk minulých let |
| net income / profit for the year | výsledek hospodaření / zisk za období |
| gross profit | hrubý zisk |
| cost of sales | náklady na prodej |
| opening balance | počáteční zůstatek |
| closing balance | konečný zůstatek |
| balance | zůstatek |
| movement | obrat |
| debit / credit | má dáti (MD) / dal (D) |
| draft | koncept |
| post / posted | zaúčtovat / zaúčtováno |
| book (an invoice), booking | zaúčtovat, zaúčtování |
| booking defaults | výchozí zaúčtování |
| booking engine | modul zaúčtování |
| void / voided | stornovat / stornováno |
| reversal (entry) | storno zápis |
| gap (line awaiting an account) | nevyřešený řádek (řádek čekající na účet) |
| blocker | blokující problém |
| accounting period / period | účetní období / období |
| fiscal year / FY | fiskální rok / fisk. rok |
| fiscal year start | začátek fiskálního roku |
| year to date (YTD) | od začátku roku (kumulativně) |
| year-end closing | roční uzávěrka |
| close / reopen a period | uzavřít / znovu otevřít |
| closing checklist | kontrolní seznam uzávěrky |
| bank reconciliation | bankovní odsouhlasení |
| match / unmatch / matched | spárovat / zrušit spárování / spárováno |
| partially matched | částečně spárováno |
| match group | skupina párování |
| auto-match | automatické párování |
| bank statement | bankovní výpis |
| bank line | bankovní pohyb (řádek výpisu) |
| bank account | bankovní účet |
| counterparty | protistrana |
| accounts payable / receivable (AP / AR) | závazky vůči dodavatelům / pohledávky za odběrateli |
| AP / AR aging | věková struktura závazků / pohledávek |
| aging bucket / "Current" bucket | věkové pásmo / do splatnosti |
| supplier / vendor | dodavatel |
| customer / client | odběratel |
| invoice | faktura |
| sales invoice / purchase invoice (bill) | vydaná faktura / přijatá faktura |
| receipt | účtenka |
| payment | platba |
| payment in / out | příchozí platba / odchozí platba |
| payer / payee | plátce / příjemce |
| payment method | způsob platby |
| bank transfer / check / credit card / cash | bankovní převod / šek / platební karta / hotovost |
| due date / issue date | datum splatnosti / datum vystavení |
| amount / total | částka / celkem |
| net amount / gross amount | částka bez daně / částka včetně daně |
| currency | měna |
| base currency | základní měna |
| exchange rate | směnný kurz (kurz) |
| exchange rate override (per company) | vlastní kurz společnosti |
| exchange difference / gain / loss | kurzový rozdíl / kurzový zisk / kurzová ztráta |
| exchange clearing account | zúčtovací účet kurzových operací |
| categorization rule | pravidlo kategorizace |
| bank-line rule | pravidlo pro bankovní pohyby |
| pattern | vzor |
| split (across accounts) | rozúčtovat, rozúčtování |
| fixed asset | dlouhodobý majetek |
| depreciation / accumulated depreciation | odpisy / oprávky |
| depreciation charge | odpis |
| useful life / salvage value / book value | doba použitelnosti / zbytková hodnota / zůstatková cena |
| straight-line / declining balance | rovnoměrné / degresivní |
| asset register | evidence majetku |
| expense sheet | výkaz výdajů |
| reimbursement | proplacení |
| expense (one claim line) | výdaj |
| employee | zaměstnanec |
| approve / reject / submit | schválit / zamítnout / odeslat ke schválení |
| VAT | DPH |
| GST / GST-HST | GST (daň ze zboží a služeb) / GST-HST |
| sales tax / consumption tax | daň z prodeje / daň ze spotřeby |
| output VAT / input VAT | DPH na výstupu / DPH na vstupu |
| VAT payable / VAT credit | DPH k úhradě / nadměrný odpočet |
| credit brought forward / carried forward | převedený nadměrný odpočet / nadměrný odpočet k převodu |
| surcharge (China, on VAT) | přirážka k DPH |
| corporate income tax (CIT) | daň z příjmů právnických osob (DPPO) |
| individual income tax (IIT) | daň z příjmů fyzických osob (DPFO) |
| profits tax (Hong Kong) | daň ze zisku |
| provisional tax | záloha na daň |
| prepaid tax (asset) | zaplacené zálohy na daň |
| assessment notice / demand note | platební výměr / výzva k úhradě zálohy |
| tax return / filing | daňové přiznání / podání |
| accrual entry (tax) | zápis zaúčtování daně |
| settlement entry (VAT) | zápis vypořádání |
| settle (a filing) | vypořádat |
| add-back / deduction | položka zvyšující základ daně / položka snižující základ daně |
| tax computation adjustments | úpravy základu daně |
| assessable profit | základ daně |
| losses brought forward | daňové ztráty minulých let |
| tiered / two-tier rates | pásmové sazby / dvoupásmová sazba |
| tax role mapping / mapped | přiřazení účtů / přiřazeno |
| template | šablona |
| company | společnost |
| legal entity name | obchodní firma |
| business card | vizitka |
| extraction (AI) | vytěžení dat |
| confidence | spolehlivost |
| needs review / mark reviewed | ke kontrole / označit jako zkontrolované |
| reprocess | znovu zpracovat |
| anonymise / personal data | anonymizovat / osobní údaje |
| document | dokument |
| tag | štítek |
| custom field | vlastní pole |
| correspondent | korespondent |
| document type | typ dokumentu |
| workflow | pracovní postup |
| owner | vlastník |
| permissions / group / role | oprávnění / skupina / role |
| company roles: viewer / accountant / admin | čtenář / účetní / správce |
| admin / superadmin (Gnos3 tiers) | administrátor / superadministrátor |
| dashboard | nástěnka |
| settings | nastavení |
| save / cancel | uložit / zrušit |
| delete / remove | smazat / odebrat |
| edit | upravit |
| search / filter | hledat / filtrovat (noun: filtr) |
| export / import | exportovat / importovat |
| upload / download | nahrát / stáhnout |
| apply / confirm | použít / potvrdit |
| loading | načítání… |
| error / warning | chyba / upozornění |
| retry / refresh | zkusit znovu / obnovit |
| preview / details | náhled / podrobnosti |
| reference (entry number) | číslo dokladu |
| description | popis |
