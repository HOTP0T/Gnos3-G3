# Gnos3 business modules — Latvian (lv-LV) glossary

## Conventions

- **Form of address**: polite plural "jūs" forms in sentences, instructions and questions ("Izvēlieties uzņēmumu", "Augšupielādējiet failu", "Vai vēlaties turpināt?"), as Open WebUI's Latvian file does ("Ievadiet…", "Atstājiet tukšu…"). "jūs / jūsu" lowercase inside sentences.
- **Buttons and menu items**: infinitive, short ("Saglabāt", "Dzēst", "Izveidot grāmatojumu", "Augšupielādēt", "Eksportēt"), as Open WebUI and K4mi do. Status words are past passive participles agreeing with the noun they describe ("Iegrāmatots", "Anulēts", "Sasaistīts"; a feminine noun takes "-a": "atskaite apstiprināta").
- **Case**: sentence case; only the first word and proper names capitalised. ALL-CAPS statement totals stay in capitals.
- **Punctuation**: Latvian quotation marks „…“ for quoted UI labels and names („{{name}}“). No space before ":" "?" "!". Ellipsis "…". A comma before subordinate clauses (ka, kas, kurš, ja, kad, lai, jo…), as Latvian grammar requires. "e.g." → "piem.", "i.e." → "t. i.", "etc." → "u. c." / "utt.", "incl." → "t. sk.", "approx." → "apm.", "no." → "Nr.".
- **Numbers and dates**: decimal comma (1 234,56), space as thousands separator; dates dd.mm.gggg. (30.10.2026.) or "2026. gada 30. oktobris"; 24-hour time. Percent with a space: "20 %". DR / CR → **D / K** (debets / kredīts).
- **Placeholders**: Latvian nouns inflect; when a placeholder holds a noun that would need another case, restructure so the placeholder stays in the nominative ("Konts: {{name}}", "{{tax}} (deklarācija)", "uzņēmumam {{name}}" — the noun before it carries the case).
- **Product names** stay as they are: Gnos3, K4mi, SmartOffice, Ollama, Open WebUI, Excel, PDF, CSV, currency codes, units.
- **Verbs that look alike**: *Confirm* = "Apstiprināt"; *Approve* (expense sheets) = "Apstiprināt" too (the screen makes the sense clear); *Post* (ledger) = "Iegrāmatot"; *Void* = "Anulēt" (never "Atcelt", which is *Cancel*); *Apply* = "Lietot" (not "Pielietot"); *Discard* = "Atmest".

## Accounting and finance

| English | Latvian |
|---|---|
| account (ledger; key `Account_gnos3`) | konts |
| account name | konta nosaukums |
| account code | konta kods |
| account type | konta veids |
| chart of accounts | kontu plāns |
| control account (with sub-accounts) | sintētiskais konts |
| sub-account | apakškonts |
| detail / leaf account | analītiskais konts |
| journal entry / entry / transaction | grāmatojums |
| journal entries (tab) | grāmatojumi |
| line (of an entry) | grāmatojuma rinda |
| journal | žurnāls |
| general ledger | virsgrāmata |
| sub-ledger | palīgvirsgrāmata |
| trial balance | apgrozījuma bilance |
| balance sheet | bilance |
| income statement / profit and loss / P&L | peļņas vai zaudējumu aprēķins |
| statement of financial position (HK) | finanšu stāvokļa pārskats |
| statement of profit or loss (HK) | peļņas vai zaudējumu pārskats |
| assets / current assets / non-current assets | aktīvi / apgrozāmie līdzekļi / ilgtermiņa ieguldījumi |
| liabilities / current / non-current | saistības / īstermiņa saistības / ilgtermiņa saistības |
| equity | pašu kapitāls |
| retained earnings | nesadalītā peļņa |
| revenue | ieņēmumi |
| income (other income) | ienākumi (citi ienākumi) |
| expenses (account type, P&L, dashboards) | izmaksas |
| cost of sales | pārdotās produkcijas izmaksas |
| administrative expenses | administrācijas izmaksas |
| finance costs | finanšu izmaksas |
| gross profit / net income | bruto peļņa / neto peļņa |
| opening balance | sākuma atlikums |
| closing balance (key `Closing_balance`) | beigu atlikums |
| balance | atlikums |
| debit / credit | debets / kredīts (D / K) |
| draft | melnraksts |
| post / posted | iegrāmatot / iegrāmatots |
| book (an invoice), booking | iegrāmatot, grāmatošana |
| booking defaults | grāmatošanas noklusējumi |
| void / voided | anulēt / anulēts |
| reversal (entry) | stornēšana (stornēšanas grāmatojums) |
| accounting period / period | grāmatvedības periods / periods |
| fiscal year / FY | finanšu gads / FG |
| year-end closing | gada slēgšana |
| year to date (YTD) | kopš gada sākuma |
| close / reopen a period | slēgt / atkārtoti atvērt |
| closing checklist | slēgšanas pārbaudes |
| blocker | šķērslis |
| gap (line awaiting an account) | trūkstošs konts / rinda bez konta |
| bank reconciliation | bankas saskaņošana |
| reconcile | saskaņot |
| match / unmatch / matched | sasaistīt / atsaistīt / sasaistīts |
| match group | sasaistes grupa |
| bank statement | bankas izraksts |
| bank line | bankas izraksta rinda |
| bank account | bankas konts |
| counterparty | darījuma partneris |
| accounts payable / receivable | kreditoru parādi / debitoru parādi |
| AP / AR aging | kreditoru / debitoru parādu vecuma analīze |
| aging bucket / "Current" bucket | vecuma grupa / termiņš nav iestājies |
| supplier / vendor | piegādātājs |
| customer / client | klients |
| invoice | rēķins |
| bill (supplier invoice) | piegādātāja rēķins |
| receipt (expense receipt) | čeks |
| payment / payment in / out | maksājums / ienākošais / izejošais maksājums |
| payer / payee | maksātājs / saņēmējs |
| payment method | maksājuma veids |
| bank transfer / cheque / credit card / cash | bankas pārskaitījums / bankas čeks / kredītkarte / skaidra nauda |
| currency / base currency | valūta / bāzes valūta |
| exchange rate | valūtas kurss |
| exchange difference / gain / loss | valūtas kursa starpība / peļņa / zaudējumi no valūtas kursa svārstībām |
| exchange clearing account | valūtas tranzītkonts |
| override (company rate) | uzņēmuma kurss (aizstāj kopējo) |
| categorization rule | kategorizēšanas noteikums |
| bank-line rule | bankas rindas noteikums |
| pattern | šablons |
| split (across accounts) | sadalīt, sadalījums |
| fixed asset | pamatlīdzeklis |
| depreciation / accumulated depreciation | nolietojums / uzkrātais nolietojums |
| useful life / salvage value / book value | lietderīgās lietošanas laiks / atlikusī vērtība / bilances vērtība |
| linear / declining | lineārā / dilstošā atlikuma metode |
| asset register | pamatlīdzekļu reģistrs |
| expense sheet / reimbursement sheet | izdevumu atskaite |
| expense (one claim line) | izdevumi (izdevumu pozīcija) |
| expenses (the expense-claims tab, key `Expenses_tab`) | izdevumu atskaites |
| reimbursement | atmaksa |
| employee | darbinieks |
| approve / reject / submit | apstiprināt / noraidīt / iesniegt |
| VAT / GST / GST-HST / sales tax / consumption tax | PVN / preču un pakalpojumu nodoklis (GST) / GST/HST / tirdzniecības nodoklis / patēriņa nodoklis |
| output / input VAT | aprēķinātais PVN / priekšnodoklis |
| VAT payable / VAT credit | maksājamais PVN / PVN pārmaksa |
| credit brought / carried forward | pārnestā pārmaksa / uz nākamo periodu pārnesamā pārmaksa |
| surcharge (China, on VAT) | piemaksa |
| urban construction tax / education surcharge | pilsētu būvniecības nodoklis / izglītības piemaksa |
| corporate income tax (CIT) | uzņēmumu ienākuma nodoklis (UIN) |
| individual income tax (IIT) | iedzīvotāju ienākuma nodoklis (IIN) |
| profits tax (Hong Kong) | peļņas nodoklis |
| provisional tax | provizoriskais nodoklis |
| prepaid tax (asset) | avansā samaksātais nodoklis |
| assessment notice / demand note | nodokļa novērtējuma paziņojums / maksājuma paziņojums |
| tax return / filing | deklarācija |
| accrual entry (tax) | uzkrājuma grāmatojums |
| settlement entry (VAT) | nokārtošanas grāmatojums |
| settle (CIT filing) | nokārtot |
| add-back / deduction | pieskaitījums / atskaitījums |
| tax computation adjustments | nodokļa aprēķina korekcijas |
| assessable profit | apliekamā peļņa |
| losses brought forward | iepriekšējo gadu zaudējumi |
| tiered rates | pakāpeniskās likmes |
| tax role mapping / mapped | piesaiste / piesaistīts |
| template | veidne |
| company | uzņēmums |
| legal entity name | juridiskais nosaukums |
| business card | vizītkarte |
| needs review / mark reviewed | jāpārbauda / atzīmēt kā pārbaudītu |
| amount / total / net / gross | summa / kopā / neto / bruto |

## Documents (K4mi)

| English | Latvian |
|---|---|
| document | dokuments |
| tag (document tag; Open WebUI chat tags stay "tagi") | birka |
| custom field | pielāgotais lauks |
| correspondent | korespondents |
| document type | dokumenta veids |
| storage path | glabāšanas ceļš |
| workflow | darbplūsma |
| owner | īpašnieks |
| inbox | iesūtne |
| archive serial number (ASN) | arhīva sērijas numurs (ASN) |
| saved view | saglabātais skats |
| original file / archived file | oriģinālais fails / arhivētais fails |
| OCR | OCR (teksta atpazīšana) |

## Interface

| English | Latvian |
|---|---|
| settings | iestatījumi |
| dashboard | infopanelis |
| save / cancel / delete / edit | saglabāt / atcelt / dzēst / rediģēt |
| create / add / remove | izveidot / pievienot / noņemt |
| search / filter | meklēt / filtrēt (noun: filtrs) |
| export / import | eksportēt / importēt |
| upload / download | augšupielādēt / lejupielādēt |
| apply | lietot |
| confirm | apstiprināt |
| discard | atmest |
| reset | atiestatīt |
| refresh / reload | atsvaidzināt / pārlādēt |
| retry | mēģināt vēlreiz |
| loading… | ielādē… |
| saving… | saglabā… |
| error / warning | kļūda / brīdinājums |
| permissions / group / user / role | atļaujas / grupa / lietotājs / loma |
| admin / superadmin | administrators / galvenais administrators |
| module | modulis |
| anonymise / decrypt | anonimizēt / atšifrēt |
| preview | priekšskatījums |
| status | statuss |
| required / optional | obligāts / neobligāts |
| enabled / disabled | iespējots / atspējots |
| chat / knowledge / workspace | tērzēšana / zināšanas / darba vide |
