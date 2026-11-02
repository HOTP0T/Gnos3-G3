# Gnos3 business modules — Basque (eu-ES) glossary

## Conventions

- **Form of address**: "zu" (standard, polite-neutral) everywhere; never "hi" / hika. Questions and instructions in the "zu" form: "Ziur zaude?", "Hautatu enpresa bat", "Saiatu berriro".
- **Buttons and menu items**: verb first, in the bare participle form, as Open WebUI's Basque file does ("Gorde", "Ezabatu", "Sortu idazpena", "Inportatu laburpena", "Bilatu txatak"). Titles and labels are noun phrases ("Idazpen berria", "Kontu-plana").
- **Case**: sentence case. Only the first word and proper names are capitalised; product names stay as they are (Gnos3, K4mi, SmartOffice, Ollama, Open WebUI, Excel, PDF, CSV). ALL-CAPS statement totals stay in capitals.
- **Placeholders** ({{name}}, {name}): Basque declines by suffix, so never glue a case ending to a placeholder. Put the placeholder in the absolutive, or after an appositive noun that takes the ending: "{{code}} kontua ez da existitzen", "{{name}} enpresaren datuak", "«{{name}}» kendu egingo da". A number placeholder precedes its noun without plural mark: "{{count}} faktura", "{{n}} lerro". When a suffix is unavoidable, attach it with a hyphen: "{{year}}-(e)ko".
- **Acronyms**: declined directly, as read aloud (Euskaltzaindia): "BEZa", "BEZaren", "SZaren"; in compounds with a hyphen: "BEZ-aitorpena", "SZ-aitorpena". Foreign acronyms take a hyphen: "PDF-a", "CSV-ko", "IBAN-a".
- **Quotes**: « » for quoted UI labels and names ("«Gorde» sakatu"); " " inside them if ever needed.
- **Punctuation**: no space before ":" "?" "!"; no inverted marks. Ellipsis as three dots "..." like the Open WebUI file ("Kargatzen...").
- **"e.g."** → "adib.:"; **"etc."** → "etab."; **"N/A"** → "E/E" (ez dagokio); **DR / CR** → Z / H (zorra / hartzekoa).
- **Numbers**: decimal comma, thousands point (1.234,56) — the app formats them; percentages "% 20" in prose is formal Basque but the UI keeps "20%" as the app prints it.
- **Dates**: year first: 2026-10-30 or "2026ko urriaren 30a"; "{{year}} ekitaldia" (not "{{year}}ko ekitaldia" unless unavoidable). Months and weekdays come from the app's locale formatter.
- **Taxes**: named from the tax kind in the UI language: VAT = BEZ, GST = GST (acronym kept; "ondasun eta zerbitzuen gaineko zerga" when spelled out), GST/HST = GST/HST, sales tax = salmenten gaineko zerga, consumption tax = kontsumoaren gaineko zerga, CIT = sozietateen gaineko zerga (SZ), profits tax = mozkinen gaineko zerga. A `{{tax}}` placeholder is placed so that it needs no suffix ("Zerga: {{tax}}", "{{tax}} aitorpena").
- **Expenses**: "gastuak" for the account type / P&L / dashboards; "gastu-orriak" for the expense-claims tab and settings group (key `Expenses_tab`).

## Accounting and finance

| English | Basque |
|---|---|
| account (ledger) | kontua |
| account code / account name | kontu-kodea / kontuaren izena |
| chart of accounts | kontu-plana |
| control account (with sub-accounts) | kontrol-kontua |
| sub-account | azpikontua |
| detail / leaf account | xehetasun-kontua (azken mailakoa) |
| journal entry / entry / transaction | idazpena |
| journal | egunkaria |
| general ledger | liburu nagusia |
| sub-ledger | liburu laguntzailea |
| trial balance | egiaztapen-balantzea |
| balance sheet | balantzea |
| profit and loss / income statement / P&L | galdu-irabazien kontua |
| statement of financial position (HK) | finantza-egoeraren egoera-orria |
| statement of profit or loss (HK) | galdu-irabazien egoera-orria |
| assets / liabilities | aktiboa / pasiboa |
| current / non-current assets | aktibo arrunta / aktibo ez-arrunta |
| current / non-current liabilities | pasibo arrunta / pasibo ez-arrunta |
| equity | ondare garbia |
| retained earnings | aurreko ekitaldietako emaitzak |
| revenue / income | diru-sarrerak |
| expenses (account type) | gastuak |
| cost of sales | salmenten kostua |
| gross profit | mozkin gordina |
| net income / profit for the year | ekitaldiko emaitza |
| opening balance | hasierako saldoa (idazpena: irekiera-idazpena) |
| closing balance | amaierako saldoa |
| balance | saldoa |
| debit / credit | zorra / hartzekoa |
| draft | zirriborroa |
| post / posted | kontabilizatu / kontabilizatua |
| book (an invoice) / booking | erregistratu / erregistroa |
| booking defaults | erregistro lehenetsiak |
| void / voided | baliogabetu / baliogabetua ("Baliogabetu idazpena", never "Utzi") |
| reversal entry | kontraidazpena |
| accounting period | kontabilitate-aldia |
| fiscal year / FY | ekitaldia |
| year-end closing | ekitaldi-itxiera |
| year to date (YTD) | ekitaldiko metatua |
| close / reopen a period | itxi / berrireki |
| closing checklist | itxiera aurreko egiaztapenak |
| blocker | eragozpena |
| gap (line awaiting an account) | zain dagoen lerroa |
| bank reconciliation | banku-bateratzea |
| match / unmatch / matched | parekatu / parekatzea desegin / parekatua |
| match group | parekatze-taldea |
| bank statement / bank line | banku-laburpena / banku-lerroa |
| bank account | banku-kontua |
| counterparty | kontrapartida |
| accounts payable / receivable | ordaintzeko kontuak / kobratzeko kontuak |
| AP / AR aging | ordaintzekoen / kobratzekoen antzinatasuna |
| supplier / vendor | hornitzailea |
| customer / client | bezeroa |
| bill (supplier invoice) | hornitzailearen faktura |
| invoice | faktura |
| invoice number / due date | faktura-zenbakia / mugaeguna |
| receipt (expense proof) | ordainagiria |
| payment | ordainketa |
| payment in / out | kobrantza / ordainketa |
| payer / payee | ordaintzailea / onuraduna |
| payment method | ordainketa-modua |
| bank transfer / check / credit card / cash | banku-transferentzia / txekea / kreditu-txartela / eskudirua |
| amount / net / gross | zenbatekoa / garbia / gordina |
| currency | moneta |
| base currency | oinarrizko moneta |
| exchange rate | truke-tasa |
| exchange difference / gain / loss | truke-diferentzia / truke-irabazia / truke-galera |
| exchange clearing account | truke-igarotze kontua |
| override (company rate) | berariazko tasa |
| categorization rule | sailkapen-araua |
| bank-line rule | banku-lerroen araua |
| pattern | eredua |
| split (across accounts) | banatu / banaketa |
| fixed asset | ibilgetua |
| depreciation / accumulated depreciation | amortizazioa / amortizazio metatua |
| useful life / salvage value / book value | bizitza baliagarria / hondar-balioa / kontabilitate-balioa |
| asset register | ibilgetuen erregistroa |
| expense | gastua |
| expense sheet | gastu-orria |
| reimbursement | itzulketa |
| employee | langilea |
| approve / reject / submit | onartu / baztertu / bidali |
| company | enpresa |
| legal entity name | izen soziala |
| template | txantiloia |
| VAT | BEZ (balio erantsiaren gaineko zerga) |
| GST / sales tax / consumption tax | GST / salmenten gaineko zerga / kontsumoaren gaineko zerga |
| output VAT / input VAT | BEZ jasanarazia / BEZ jasana |
| VAT payable / VAT credit | ordaintzeko BEZa / BEZaren aldeko saldoa |
| credit brought / carried forward | aurreko aldiko saldoa / hurrengo aldirako saldoa |
| surcharge (China) | zerga gehigarria |
| corporate income tax (CIT) | sozietateen gaineko zerga (SZ) |
| individual income tax (IIT) | pertsona fisikoen errentaren gaineko zerga (PFEZ) |
| profits tax (Hong Kong) | mozkinen gaineko zerga |
| provisional tax | behin-behineko zerga |
| prepaid tax (asset) | aurretik ordaindutako zerga |
| assessment notice / demand note | likidazio-jakinarazpena / ordainketa-eskaera |
| tax return / filing | aitorpena |
| accrual entry | sortzapen-idazpena |
| settlement entry / settle | likidazio-idazpena / likidatu |
| add-back / deduction | gehikuntza / kenkaria |
| tax adjustments | zerga-doikuntzak |
| assessable profit | mozkin zergagarria |
| losses brought forward | konpentsatzeko galerak |
| tax role mapping / mapped | esleipena / esleitua |
| business card | bisita-txartela |
| needs review / mark reviewed | berrikusteko / markatu berrikusitzat |
| report | txostena |

## Documents (K4mi)

| English | Basque |
|---|---|
| document | dokumentua |
| tag | etiketa |
| custom field | eremu pertsonalizatua |
| correspondent | korrespondentea |
| document type | dokumentu mota |
| storage path | biltegiratze-bidea |
| upload | kargatu |
| workflow | lan-fluxua |
| saved view | gordetako ikuspegia |
| owner | jabea |
| archive serial number (ASN) | artxiboko serie-zenbakia (ASN) |
| inbox | sarrera-ontzia |
| OCR | OCR |

## Interface words

| English | Basque |
|---|---|
| settings | ezarpenak |
| dashboard | aginte-panela |
| save / cancel / delete / edit | gorde / utzi / ezabatu / editatu |
| search / filter | bilatu / iragazi |
| export / import | esportatu / inportatu |
| upload / download | kargatu / deskargatu |
| apply / confirm | aplikatu / berretsi |
| create / add / remove | sortu / gehitu / kendu |
| close / open | itxi / ireki |
| loading... | kargatzen... |
| error / warning | errorea / abisua |
| status | egoera |
| date | data |
| total | guztira |
| refresh | freskatu |
| retry | saiatu berriro |
| preview | aurrebista |
| optional / required | aukerakoa / derrigorrezkoa |
| permissions / group / user | baimenak / taldea / erabiltzailea |
| admin | administratzailea |
| language | hizkuntza |
