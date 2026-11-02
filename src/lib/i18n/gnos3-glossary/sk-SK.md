# Gnos3 business modules — Slovak (sk-SK) glossary

## Conventions

- **Register**: formal "vy" (vykanie), lowercase in running text ("Vyberte účet", "Zadajte kurz"). Never tykanie.
- **Buttons and menu items**: infinitive ("Uložiť", "Vytvoriť zápis", "Zaúčtovať", "Stornovať zápis"). Instructions in messages: polite imperative plural ("Vyberte…", "Skontrolujte…", "Skúste to znova").
- **Case**: sentence case — only the first word and proper names capitalised ("Predvolené zaúčtovanie", not "Predvolené Zaúčtovanie"). ALL-CAPS statement totals stay in capitals.
- **Punctuation**: no space before ":" "?" "!"; Slovak quotes „…“ for quoted UI labels and names; spaced en dash " – " for asides; "…" (one character) for "loading…"; "napr." for "e.g.", "t. j." for "i.e.", "atď." for "etc."; arrows "→" in paths stay ("Nastavenia → Kurzy").
- **Numbers and dates**: decimal comma, (non-breaking) space as thousands separator (1 234,56); date d. M. yyyy (30. 10. 2026); percentages with a space ("15 %"). Currency codes (EUR, USD, HKD, CNY) and units stay as they are.
- **MD / D**: debit = má dať (MD), credit = dal (D). Column headers "MD" / "D"; DR / CR in the source → MD / D.
- **Placeholders**: Slovak declines nouns; build sentences so a `{{name}}` / `{name}` stays in the nominative — apposition after a noun ("účet {{code}}", "spoločnosť „{{name}}“") or after a colon ("Chýba účet: {{code}}").
- **Counts**: Slovak has three plural forms (1 / 2–4 / 5+). For a bare `{{count}} rows` prefer a neutral form "Riadky: {{count}}" / "Počet riadkov: {{count}}"; when a key is explicitly singular ("1 row") or plural, use the matching form, with 5+ (genitive plural) as the default plural.
- **Tax names** inserted as `{{tax}}` / `{tax}`: treat as feminine ("DPH", "daň") and avoid declining them — "{{tax}} na výstupe", "priznanie ({{tax}})", "{{tax}}: priznanie".
- **Product names** stay: Gnos3, K4mi, SmartOffice, Ollama, Open WebUI, Excel, PDF, CSV.
- **Delete vs Remove**: Delete = Odstrániť (destroys data, as Open WebUI's Slovak file), Remove = Odobrať (takes out of a list / unassigns). Void = Stornovať (never "Zrušiť", which is Cancel).
- **AI** stays "AI" (umelá inteligencia), e.g. "Návrh AI", "Kategorizovať (AI)".

## Terms

| English | Slovak |
|---|---|
| account (ledger) | účet |
| account name | názov účtu |
| account code | číslo účtu |
| chart of accounts | účtový rozvrh |
| control account (with sub-accounts) | syntetický účet |
| sub-account | analytický účet (podúčet) |
| detail / leaf account | koncový účet |
| account type | typ účtu |
| assets / liabilities / equity | aktíva / záväzky / vlastné imanie |
| revenue / income | výnosy |
| expenses (account type, P&L, dashboards) | náklady |
| expenses (expense-claims tab, key `Expenses_tab`) | výdavky zamestnancov |
| journal entry / entry / transaction | účtovný zápis / zápis |
| journal | účtovný denník |
| voucher (manual entry document) | účtovný doklad |
| general ledger | hlavná kniha |
| sub-ledger | pomocná kniha |
| trial balance | obratová súvaha |
| balance sheet | súvaha |
| income statement / P&L / profit & loss | výkaz ziskov a strát |
| statement of financial position (HK) | výkaz o finančnej situácii |
| statement of profit or loss (HK) | výkaz ziskov alebo strát |
| current / non-current assets | krátkodobé / dlhodobé aktíva |
| current / non-current liabilities | krátkodobé / dlhodobé záväzky |
| retained earnings | nerozdelený zisk minulých rokov |
| net income / profit for the year | výsledok hospodárenia / zisk za obdobie |
| gross profit | hrubý zisk |
| cost of sales | náklady na predaj |
| opening balance | počiatočný stav |
| closing balance | konečný stav |
| balance | zostatok |
| movement | obrat |
| debit / credit | má dať (MD) / dal (D) |
| draft | koncept |
| post / posted | zaúčtovať / zaúčtované |
| book (an invoice), booking | zaúčtovať, zaúčtovanie |
| booking defaults | predvolené zaúčtovanie |
| booking engine | modul zaúčtovania |
| void / voided | stornovať / stornované |
| reversal (entry) | stornovací zápis |
| gap (line awaiting an account) | nevyriešený riadok (riadok čakajúci na účet) |
| blocker | blokujúci problém |
| accounting period / period | účtovné obdobie / obdobie |
| fiscal year / FY | účtovný rok / úč. rok |
| fiscal year start | začiatok účtovného roka |
| year to date (YTD) | od začiatku roka (kumulatívne) |
| year-end closing | ročná závierka |
| close / reopen a period | uzavrieť / znova otvoriť |
| closing checklist | kontrolný zoznam závierky |
| bank reconciliation | bankové odsúhlasenie |
| match / unmatch / matched | spárovať / zrušiť spárovanie / spárované |
| partially matched | čiastočne spárované |
| match group | skupina párovania |
| auto-match | automatické párovanie |
| bank statement | bankový výpis |
| bank line | bankový pohyb (riadok výpisu) |
| bank account | bankový účet |
| counterparty | protistrana |
| accounts payable / receivable (AP / AR) | záväzky voči dodávateľom / pohľadávky voči odberateľom |
| AP / AR aging | veková štruktúra záväzkov / pohľadávok |
| aging bucket / "Current" bucket | vekové pásmo / v lehote splatnosti |
| supplier / vendor | dodávateľ |
| customer / client | odberateľ |
| invoice | faktúra |
| sales invoice / purchase invoice (bill) | vydaná faktúra / prijatá faktúra |
| receipt | účtenka (pokladničný doklad) |
| payment | platba (úhrada) |
| payment in / out | prijatá platba / odoslaná platba |
| payer / payee | platiteľ / príjemca |
| payment method | spôsob platby |
| bank transfer / check / credit card / cash | bankový prevod / šek / platobná karta / hotovosť |
| due date / issue date | dátum splatnosti / dátum vystavenia |
| amount / total | suma / spolu |
| net amount / gross amount | suma bez dane / suma s daňou |
| currency | mena |
| base currency | základná mena |
| exchange rate | výmenný kurz (kurz) |
| exchange rate override (per company) | vlastný kurz spoločnosti |
| exchange difference / gain / loss | kurzový rozdiel / kurzový zisk / kurzová strata |
| exchange clearing account | zúčtovací účet kurzových operácií |
| categorization rule | pravidlo kategorizácie |
| bank-line rule | pravidlo pre bankové pohyby |
| pattern | vzor |
| split (across accounts) | rozúčtovať, rozúčtovanie |
| fixed asset | dlhodobý majetok |
| depreciation / accumulated depreciation | odpisy / oprávky |
| depreciation charge | odpis |
| useful life / salvage value / book value | doba použiteľnosti / zvyšková hodnota / zostatková cena |
| straight-line / declining balance | rovnomerné / degresívne |
| asset register | evidencia majetku |
| expense sheet | výkaz výdavkov |
| reimbursement | preplatenie (náhrada výdavkov) |
| expense (one claim line) | výdavok |
| employee | zamestnanec |
| approve / reject / submit | schváliť / zamietnuť / odoslať na schválenie |
| VAT | DPH |
| GST / GST-HST | GST (daň z tovarov a služieb) / GST-HST |
| sales tax / consumption tax | daň z predaja / spotrebná daň |
| output VAT / input VAT | DPH na výstupe / DPH na vstupe |
| VAT payable / VAT credit | DPH na úhradu (daňová povinnosť) / nadmerný odpočet |
| credit brought forward / carried forward | prenesený nadmerný odpočet / nadmerný odpočet na prenesenie |
| surcharge (China, on VAT) | prirážka k DPH |
| corporate income tax (CIT) | daň z príjmov právnických osôb (DPPO) |
| individual income tax (IIT) | daň z príjmov fyzických osôb (DPFO) |
| profits tax (Hong Kong) | daň zo zisku |
| provisional tax | preddavok na daň |
| prepaid tax (asset) | zaplatené preddavky na daň |
| assessment notice / demand note | platobný výmer / výzva na úhradu preddavku |
| tax return / filing | daňové priznanie / podanie |
| accrual entry (tax) | zápis zaúčtovania dane |
| settlement entry (VAT) | zápis vysporiadania |
| settle (a filing) | vysporiadať |
| add-back / deduction | položka zvyšujúca základ dane / položka znižujúca základ dane |
| tax computation adjustments | úpravy základu dane |
| assessable profit | základ dane |
| losses brought forward | daňové straty z minulých rokov |
| tiered / two-tier rates | pásmové sadzby / dvojpásmová sadzba |
| tax role mapping / mapped | priradenie účtov / priradené |
| template | šablóna |
| company | spoločnosť |
| legal entity name | obchodné meno |
| business card | vizitka |
| extraction (AI) | vyťaženie údajov |
| confidence | spoľahlivosť |
| needs review / mark reviewed | na kontrolu / označiť ako skontrolované |
| reprocess | znova spracovať |
| anonymise / personal data | anonymizovať / osobné údaje |
| document | dokument |
| tag | štítok |
| custom field | vlastné pole |
| correspondent | odosielateľ |
| document type | typ dokumentu |
| storage path | cesta k úložisku |
| workflow | pracovný postup |
| owner | vlastník |
| permissions / group / role | oprávnenia / skupina / rola |
| company roles: viewer / accountant / admin | čitateľ / účtovník / správca |
| admin / superadmin (Gnos3 tiers) | administrátor / superadministrátor |
| dashboard | hlavný panel |
| settings | nastavenia |
| save / cancel | uložiť / zrušiť |
| delete / remove | odstrániť / odobrať |
| edit | upraviť |
| search / filter | hľadať (noun: vyhľadávanie) / filtrovať (noun: filter) |
| export / import | exportovať / importovať |
| upload / download | nahrať / stiahnuť |
| apply / confirm | použiť / potvrdiť |
| loading | načítava sa… |
| error / warning | chyba / upozornenie |
| retry / refresh | skúsiť znova / obnoviť |
| preview / details | náhľad / podrobnosti |
| reference (entry number) | číslo dokladu |
| description | popis |
