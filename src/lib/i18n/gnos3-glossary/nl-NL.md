# Gnos3 business modules — Dutch (nl-NL) glossary

## Conventions

- **Form of address: "u"** (formal), never "je/jij": "Kies een bedrijf", "U kunt dit niet ongedaan maken". Prefer impersonal phrasing where it reads naturally ("Er is nog geen bedrijf aangemaakt").
- **Buttons and menu actions: infinitive**, object first ("Opslaan", "Boeking aanmaken", "Bestand uploaden", "Concept verwijderen"). Titles and labels: noun phrases ("Nieuwe boeking", "Instellingen bedrijf").
- **Sentence case**: only the first word and proper names get a capital ("Winst-en-verliesrekening per periode"). ALL-CAPS statement totals stay in capitals.
- **Compounds are written as one word** (Dutch rule): "bankafschrift", "btw-aangifte", "grootboekrekening", "standaardinstellingen". Use a hyphen with abbreviations, codes, numbers and product names: "btw-tarief", "K4mi-label", "PDF-bestand", "CSV-export", "EUR-rekening", "Excel-sjabloon".
- **btw** is written lower case (also "btw-nummer", "btw-aangifte"). Other tax abbreviations as the country writes them: GST, HST, ICMS, Vpb, IB.
- **Punctuation**: no space before ":" "?" "!" ";". Quoted UI labels and names in “…” (typographic double quotes). Ellipsis "…" for progress ("Laden…", "Opslaan…"). "e.g." → "bijv.", "i.e." → "d.w.z.", "etc." → "enz.", "vs." → "t.o.v." or "versus".
- **Numbers and dates**: decimal comma, thousands point (1.234,56); dates dd-mm-jjjj (30-10-2026), months lower case (oktober, ma/di/wo); "t/m" for "through" in ranges ("jan t/m mrt"). Percent without a space in running text (21%).
- **DR / CR** → **D / C** in column headers; "Debet" / "Credit" written out elsewhere.
- **Placeholders** ({{name}}, {name}, <0>) stay exactly as given; Dutch word order may move them, never drop or rename them.
- A `{{tax}}` / `{tax}` filled with a tax name (btw, GST, Vpb…) is used without article where possible ("Aangifte {{tax}}", "{{tax}}-aangifte" only if the name is short).

## Accounting and finance

| English | Dutch (nl-NL) |
|---|---|
| account (ledger) | rekening (formal: grootboekrekening) |
| account name / code | rekeningnaam / rekeningnummer |
| chart of accounts | rekeningschema |
| account type | rekeningtype |
| control account (with sub-accounts) | verzamelrekening |
| sub-account | subrekening |
| detail / leaf account | detailrekening |
| journal entry / entry / transaction (books) | boeking (journaalpost in formal contexts) |
| journal | dagboek |
| line (of an entry) | boekingsregel |
| ledger / general ledger | grootboek |
| sub-ledger | subadministratie |
| trial balance | proef- en saldibalans (short: saldibalans) |
| balance sheet | balans |
| profit and loss / income statement / P&L | winst-en-verliesrekening (W&V) |
| statement of financial position (HK) | overzicht van de financiële positie |
| statement of profit or loss (HK) | overzicht van winst of verlies |
| current / non-current assets | vlottende activa / vaste activa |
| current / non-current liabilities | kortlopende schulden / langlopende schulden |
| equity | eigen vermogen |
| retained earnings | ingehouden winst |
| revenue / income | omzet / opbrengsten |
| expense (account type, P&L) | kosten |
| cost of sales / COGS | kostprijs van de omzet |
| gross profit / net income | brutowinst / nettoresultaat |
| opening balance | beginsaldo (entries: openingsboeking) |
| closing balance | eindsaldo |
| debit / credit | debet / credit (columns: D / C) |
| draft | concept |
| post / posted | boeken / geboekt |
| book (an invoice), booking | boeken, boeking |
| booking defaults | standaardboekingen |
| void / voided | ongeldig maken / ongeldig (button: "Boeking ongeldig maken", never "Annuleren") |
| reversal (entry) | tegenboeking |
| accounting period / period | boekingsperiode / periode |
| fiscal year / FY | boekjaar / BJ |
| year-end closing | jaarafsluiting |
| year to date (YTD) | boekjaar t/m heden (column: cum. boekjaar) |
| close / reopen a period | afsluiten / heropenen |
| closing checklist | controlelijst afsluiting |
| blocker | blokkerend punt |
| gap (line awaiting an account) | openstaande regel (line still without account) |
| bank reconciliation | bankafstemming |
| match / unmatch / matched | koppelen / ontkoppelen / gekoppeld |
| auto-match | automatisch koppelen |
| match group | koppelgroep |
| bank statement / bank line | bankafschrift / bankregel |
| counterparty | tegenpartij |
| accounts payable / receivable (AP / AR) | crediteuren / debiteuren |
| AP / AR aging | ouderdomsanalyse crediteuren / debiteuren |
| aging bucket / "Current" bucket | ouderdomsklasse / niet vervallen |
| supplier / vendor | leverancier |
| customer / client | klant |
| invoice / bill (supplier invoice) | factuur / inkoopfactuur |
| sales invoice | verkoopfactuur |
| receipt (expense proof) | bon (bonnetje in the expense app) |
| payment / payment in / payment out | betaling / ontvangst / uitgaande betaling |
| payer / payee | betaler / begunstigde |
| payment method | betaalwijze |
| bank transfer / check / credit card / cash | bankoverschrijving / cheque / creditcard / contant |
| currency / base currency | valuta / basisvaluta |
| exchange rate | wisselkoers |
| exchange difference / gain / loss | koersverschil / koerswinst / koersverlies |
| exchange clearing account | tussenrekening valuta |
| rate override (company rate) | afwijkende koers |
| categorization rule | categoriseringsregel |
| bank-line rule | regel voor bankregels |
| pattern | patroon |
| split (across accounts) | verdelen, verdeling |
| fixed asset | vast actief (plural: vaste activa) |
| depreciation / accumulated depreciation | afschrijving / cumulatieve afschrijvingen |
| useful life / salvage value / book value | gebruiksduur / restwaarde / boekwaarde |
| straight-line / declining balance | lineair / degressief |
| asset register | activaregister |
| expense sheet / expense claim | declaratie (onkostendeclaratie) |
| expenses (the expense-claims tab, `Expenses_tab`) | declaraties |
| reimbursement | vergoeding |
| employee | medewerker |
| approve / reject / submit | goedkeuren / afwijzen / indienen |
| company | bedrijf |
| legal entity name | statutaire naam |
| template | sjabloon |

## Taxes

| English | Dutch (nl-NL) |
|---|---|
| VAT / tax (generic) | btw / belasting |
| GST / GST-HST / sales tax / consumption tax | GST / GST/HST / omzetbelasting (VS: sales tax) / verbruiksbelasting |
| output / input VAT | af te dragen btw / voorbelasting |
| VAT payable / VAT credit | te betalen btw / btw-tegoed |
| VAT return | btw-aangifte |
| credit brought forward / carried forward | overgebracht tegoed / over te brengen tegoed |
| surcharge (China, on VAT) | toeslag |
| corporate income tax (CIT) | vennootschapsbelasting (Vpb) |
| individual income tax (IIT) | inkomstenbelasting (IB) |
| profits tax (Hong Kong) | winstbelasting |
| provisional tax | voorlopige belasting (voorlopige aanslag) |
| prepaid tax | vooruitbetaalde belasting |
| assessment notice / demand note | aanslagbiljet / betalingsaanmaning |
| tax return / filing | aangifte |
| accrual entry (tax) | overlopende boeking (belastinglast) |
| settlement entry (VAT) | afrekeningsboeking |
| settle | afrekenen |
| add-back / deduction | bijtelling / aftrek |
| tax adjustments | fiscale correcties |
| assessable profit | belastbare winst |
| losses brought forward | compensabele verliezen |
| tiered rates / two-tier | schijventarief / tweeschijventarief |
| tax role mapping / mapped | koppeling / gekoppeld |
| due date | vervaldatum |

## Documents (K4mi)

| English | Dutch (nl-NL) |
|---|---|
| document | document |
| tag (K4mi document tag) | label (K4mi-label) |
| tag (chat / Open WebUI tag) | tag |
| custom field | aangepast veld |
| correspondent | correspondent |
| document type | documenttype |
| storage path | opslagpad |
| upload | uploaden |
| workflow | workflow |
| owner | eigenaar |
| business card | visitekaartje |
| needs review / mark reviewed | controle nodig / markeren als gecontroleerd |
| extraction / extract | extractie / uitlezen |
| reprocess | opnieuw verwerken |
| preview | voorbeeld |

## UI words

| English | Dutch (nl-NL) |
|---|---|
| settings | instellingen |
| dashboard | dashboard |
| save | opslaan |
| cancel | annuleren |
| delete / remove | verwijderen |
| edit | bewerken |
| create / add | aanmaken / toevoegen |
| search | zoeken |
| filter | filteren (noun: filter) |
| export / import | exporteren / importeren |
| download | downloaden |
| apply | toepassen |
| confirm | bevestigen |
| loading | laden… |
| saving | opslaan… |
| error / warning | fout / waarschuwing |
| refresh | vernieuwen |
| close | sluiten |
| back / next | terug / volgende |
| select | selecteren |
| clear (filters) | wissen |
| permissions | rechten |
| group / user | groep / gebruiker |
| admin / superadmin | beheerder / superbeheerder |
| status | status |
| no results | geen resultaten |
| optional / required | optioneel / verplicht |
