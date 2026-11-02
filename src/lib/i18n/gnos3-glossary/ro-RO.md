# Gnos3 business modules — Romanian (ro-RO) glossary

## Conventions

- **Form of address: formal "dumneavoastră"** in sentences, with 2nd-person-plural verbs: „Selectați o societate”, „Nu aveți acces la această pagină”, „Încercați din nou”. Use „dvs.” only where space is tight. Never the informal „tu” in messages. Impersonal phrasing where it reads naturally („Nicio societate creată încă”, „Nu se poate anula”).
- **Buttons and menu actions: short imperative (2nd person singular), object after the verb**, as Open WebUI's Romanian catalog already does: „Salvează”, „Anulează”, „Șterge”, „Editează”, „Creează înregistrarea”, „Încarcă fișierul”, „Exportă în Excel”. Titles, column headers and labels: nouns („Înregistrare nouă”, „Setări societate”, „Dată”, „Sumă”).
- **Capitalisation**: sentence case — never English title case („Contul de profit și pierdere pe perioade”, not „Contul De Profit Și Pierdere”). Months, weekdays and nationalities are lower case in Romanian („octombrie”, „luni”). ALL-CAPS statement totals stay in capitals („TOTAL ACTIVE”).
- **Diacritics**: always ș ț with comma below (U+0219, U+021B, Ș Ț), never the cedilla forms ş ţ; ă â î as usual (â inside words, î at word start/end).
- **Punctuation**: no space before „:” „?” „!” „;”. Quoted UI labels and names in „…” (U+201E … U+201D). Ellipsis „…” for progress („Se încarcă…”, „Se salvează…”). "e.g." → „de ex.”, "i.e." → „adică”, "etc." → „etc.”, "vs." → „față de”, "incl." → „incl.”, "approx." → „aprox.”. An em dash "—" used as a break stays „—” (or becomes „–” with spaces).
- **Numbers and dates**: decimal comma, thousands point (1.234,56); dates ZZ.LL.AAAA (30.10.2026); percent with no space in running text is acceptable, but prefer „19%”. Ranges „ian.–mar.”, „până la”. Romanian needs „de” between a number ≥ 20 and a noun („25 de facturi”); with a {{count}} placeholder write „{{count}} facturi” or rephrase („Facturi: {{count}}”) — never put a hard-coded „de” before a variable.
- **Debit / credit** → **debit / credit**; column headers **D / C** for DR / CR. "Debits" (verb) → „debitează”, "credits" → „creditează”.
- **Placeholders** ({{name}}, {name}, <0>…</0>) stay exactly as given; Romanian word order may move them, never drop or rename them.
- Product names unchanged: Gnos3, K4mi, SmartOffice, Ollama, Open WebUI, Excel, PDF, CSV, ISO currency codes, units.
- Tax names come from the tax kind, never the country's own label: VAT = „TVA” (feminine: „TVA colectată”), GST = „GST (taxa pe bunuri și servicii)”, GST/HST = „GST/HST”, sales tax = „taxa pe vânzări”, consumption tax = „taxa pe consum”, ICMS = „ICMS”, corporate income tax = „impozit pe profit”, Hong Kong profits tax = „impozit pe profit (Profits Tax)”. A template with {{tax}} / {tax} puts the name after a noun so gender never matters: „Declarația {{tax}}”, „Cont {{tax}} colectată” is avoided → „Cont de {{tax}} (colectare)”.
- Words with two senses on our screens: Account_gnos3 = „cont” (ledger account; a user login is „cont de utilizator”); Expenses_tab = „Deconturi” (expense claims), while expenses in the P&L are „cheltuieli”; Tax_tab = „Taxe” (the tab), while the tax amount is „taxă” / „TVA”.

## Accounting and finance

| English | Romanian (ro-RO) |
|---|---|
| account (ledger) | cont |
| account code / account name | simbol cont (short label: „Cod cont”) / denumire cont |
| account type | tip de cont |
| chart of accounts | plan de conturi |
| chart template | șablon de plan de conturi |
| control account (with sub-accounts) | cont colector (sintetic) |
| sub-account | subcont (cont analitic) |
| detail / leaf account | cont de detaliu (analitic) |
| journal entry / entry / transaction (books) | înregistrare contabilă (short: înregistrare) |
| line (of an entry) | linie (rând) de înregistrare |
| journal | jurnal |
| general ledger / ledger | Cartea mare / registrul contabil |
| sub-ledger | evidență analitică |
| trial balance | balanță de verificare |
| balance sheet | bilanț |
| profit and loss / income statement / P&L | contul de profit și pierdere |
| statement of financial position (HK) | situația poziției financiare |
| statement of profit or loss (HK) | situația profitului sau pierderii |
| assets / liabilities | active / datorii (statement headings: ACTIVE / DATORII) |
| current / non-current assets | active circulante / active imobilizate |
| current / non-current liabilities | datorii curente / datorii pe termen lung |
| equity | capitaluri proprii |
| retained earnings | rezultatul reportat |
| revenue | venituri (cifra de afaceri) |
| other income | alte venituri |
| expenses (account type, P&L) | cheltuieli |
| expenses (expense-claims tab, `Expenses_tab`) | deconturi |
| cost of sales / COGS | costul vânzărilor |
| gross profit | profit brut |
| net income / profit for the year | rezultat net / profitul exercițiului |
| opening balance | sold inițial (entries: înregistrare de deschidere) |
| closing balance | sold final |
| balance (of an account) | sold |
| debit / credit | debit / credit (D / C) |
| draft | ciornă |
| post / posted | contabilizează / contabilizată |
| book (an invoice) / booking | înregistra în contabilitate / contare |
| booking dialog | fereastra de contare |
| booking defaults | conturi implicite de contare |
| booking engine | motorul de contare |
| gap (line awaiting an account) | linie în așteptare (fără cont) |
| blocker | element blocant |
| void / voided | anulează / anulată (button „Anulează înregistrarea”, so it never reads as Cancel) |
| reversal (entry) | stornare (înregistrare de stornare) |
| accounting period | perioadă contabilă |
| fiscal year / FY | exercițiu financiar / ex. |
| year-end closing | închiderea exercițiului |
| year to date (YTD) | cumulat de la începutul exercițiului (short: cumulat) |
| close / reopen a period | închide / redeschide |
| closing checklist | verificări de închidere |
| carry forward / brought forward | reportat / preluat |
| bank reconciliation | reconciliere bancară |
| match / unmatch / matched | asociază / anulează asocierea / asociată |
| match group | grup de asociere |
| auto-match | asociere automată |
| bank account | cont bancar |
| bank statement | extras de cont |
| bank line / statement line | linie de extras |
| counterparty | contrapartidă |
| accounts payable / receivable | datorii furnizori / creanțe clienți |
| AP / AR aging | scadențar furnizori / scadențar clienți |
| aging bucket / "Current" bucket | interval de vechime / în termen |
| supplier, vendor / customer | furnizor / client |
| bill (supplier invoice) | factură de furnizor |
| invoice | factură |
| receipt (expense) | bon / chitanță (proof of expense: document justificativ) |
| payment | plată |
| payment in / out | încasare / plată |
| payer / payee | plătitor / beneficiar |
| payment method | metodă de plată |
| bank transfer / check / card / cash | transfer bancar / cec / card / numerar |
| amount / total | sumă / total |
| currency / base currency | monedă / moneda de bază |
| foreign currency | valută |
| exchange rate | curs de schimb |
| exchange difference / gain / loss | diferență de curs valutar / câștig din diferențe de curs / pierdere din diferențe de curs |
| exchange clearing account | cont de tranzit valutar |
| override (company rate) | curs specific (al societății) |
| categorization rule | regulă de clasificare |
| bank-line rule | regulă pentru liniile de extras |
| pattern | tipar |
| split (across accounts) | defalcare / defalcă |
| fixed asset | mijloc fix (imobilizare) |
| depreciation / accumulated depreciation | amortizare / amortizare cumulată |
| useful life / salvage value / book value | durată de utilizare / valoare reziduală / valoare contabilă netă |
| straight-line / declining balance | liniară / degresivă |
| asset register | registrul mijloacelor fixe |
| expense / expense sheet | cheltuială / decont de cheltuieli |
| reimbursement | rambursare |
| employee | angajat |
| approve / reject / submit | aprobă / respinge / trimite |
| company | societate |
| legal entity name | denumire legală |
| template | șablon |

## Taxes

| English | Romanian (ro-RO) |
|---|---|
| VAT / output VAT / input VAT | TVA / TVA colectată / TVA deductibilă |
| VAT payable / VAT credit (receivable) | TVA de plată / TVA de recuperat |
| credit brought forward / carried forward | sold de recuperat preluat / sold de recuperat reportat |
| surcharge (China, on VAT) | taxă suplimentară |
| urban construction tax / education surcharge | taxa de întreținere și construcție urbană / taxa suplimentară pentru educație |
| corporate income tax (CIT) | impozit pe profit |
| individual income tax (IIT) | impozit pe venit |
| profits tax (Hong Kong) | impozit pe profit (Profits Tax) |
| provisional tax | plăți anticipate de impozit |
| prepaid tax (asset) | impozit plătit în avans |
| assessment notice / demand note | decizie de impunere / notificare de plată |
| tax return / filing | declarație fiscală / depunere |
| accrual entry (tax) | înregistrare de recunoaștere a impozitului |
| settlement entry (VAT) | înregistrare de regularizare |
| settle (CIT filing) | decontează |
| add-back / deduction | adăugare (element nedeductibil) / deducere |
| tax computation adjustments | ajustări fiscale |
| adjusted / assessable profit | profit fiscal / profit impozabil |
| losses brought forward | pierderi fiscale reportate |
| two-tier / tiered rates | cote pe două trepte / cote pe tranșe |
| tax rate | cotă de impozitare (VAT: cotă de TVA) |
| tax role mapping / mapped | asociere / asociat |

## Documents (K4mi)

| English | Romanian (ro-RO) |
|---|---|
| document | document |
| tag | etichetă |
| custom field | câmp personalizat |
| correspondent | corespondent |
| document type | tip de document |
| storage path | cale de stocare |
| saved view | vizualizare salvată |
| owner | proprietar |
| note | notă |
| archive serial number (ASN) | număr serial în arhivă (ASN) |
| workflow | flux de lucru |
| upload | încărcare (button: „Încarcă”) |
| business card | carte de vizită |
| needs review / mark reviewed | de verificat / marchează ca verificat |

## UI words (as in Open WebUI's ro-RO catalog)

| English | Romanian (ro-RO) |
|---|---|
| settings | Setări |
| dashboard | Tablou de bord |
| save | Salvează |
| cancel | Anulează |
| delete | Șterge |
| edit | Editează |
| create / add / remove | Creează / Adaugă / Elimină |
| search | Caută (noun: căutare) |
| filter | Filtrează (noun: filtru) |
| export / import | Exportă / Importă |
| upload / download | Încarcă / Descarcă |
| apply | Aplică |
| confirm | Confirmă |
| close | Închide |
| refresh | Reîmprospătează |
| preview | Previzualizare |
| loading… | Se încarcă… |
| saving… | Se salvează… |
| error | Eroare |
| status | Stare |
| permissions | Permisiuni |
| group / user | grup / utilizator |
| admin / superadmin | administrator / superadministrator |
