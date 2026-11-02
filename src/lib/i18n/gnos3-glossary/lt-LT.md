# Gnos3 business modules — Lithuanian (lt-LT) glossary

## Conventions

- **Form of address**: formal plural (jūs). Instructions and messages use the 2nd person plural imperative ("Pasirinkite įmonę", "Įkelkite failą", "Ar tikrai norite tęsti?"). The pronoun "jūs / jūsų" is written in lowercase inside UI text.
- **Buttons and menu items**: the infinitive, as in Open WebUI's Lithuanian file ("Išsaugoti", "Ištrinti", "Sukurti įrašą", "Įkelti", "Eksportuoti"). Tabs and headings are nouns ("Įrašai", "Mokėjimai", "Ataskaitos"). Status words are past passive participles agreeing with the noun they describe, or neutral forms when the noun is unknown ("Užregistruota", "Anuliuota", "Suderinta").
- **Case**: sentence case; only the first word and proper names start with a capital. ALL-CAPS statement totals stay in capitals ("TURTAS", "IŠ VISO").
- **Punctuation**: Lithuanian quotation marks „…“ for quoted names and UI labels („{{name}}“). No space before ":" "?" "!". A spaced en dash " – " for parenthetical dashes. Ellipsis "…".
- **Abbreviations**: "e.g." → "pvz.", "i.e." → "t. y.", "etc." → "ir kt.", "incl." → "įskaitant", "approx." → "apie", "No." → "Nr.". DR / CR → **D / K** (debetas / kreditas). VAT → **PVM**, IIT → **GPM**.
- **Numbers and dates**: decimal comma (1 234,56) with a (non-breaking) space as thousands separator; dates in the Lithuanian standard order yyyy-mm-dd (2026-10-30); 24-hour time; percent with a space ("21 %").
- **Placeholders**: Lithuanian nouns decline (7 cases). Keep a placeholder holding a name in the nominative by restructuring: "Įmonė: {{name}}", "„{{name}}“ bus pašalinta", "sąskaita {{code}}" (the placeholder follows its head noun, which takes the case). For counts, prefer the "label: number" form ("Eilučių: {{count}}", "Pasirinkta: {{count}}"), which avoids Lithuanian's three plural forms (1 / 2–9 / 10+).
- **Invoice vs account**: "sąskaita" alone always means a ledger or bank **account**; an invoice is always **sąskaita faktūra** (pl. "sąskaitos faktūros", gen. pl. "sąskaitų faktūrų"), never shortened.
- **Distinct verbs**: *Confirm* / *Approve* = "Patvirtinti"; *Post* (to the ledger) = "Registruoti" / "Užregistruota"; *Book* (assign accounts to an invoice) = "Kontuoti" / "kontavimas"; *Void* = "Anuliuoti" (never "Atšaukti", which is *Cancel*); *Match* = "Suderinti".
- **Product names** stay as they are: Gnos3, K4mi, SmartOffice, Ollama, Open WebUI, Excel, PDF, CSV, currency codes, units.

## Accounting and finance

| English | Lithuanian |
|---|---|
| account (ledger) | sąskaita |
| account name | sąskaitos pavadinimas |
| account code | sąskaitos kodas |
| account type | sąskaitos tipas |
| chart of accounts | sąskaitų planas |
| control account (with sub-accounts) | suvestinė sąskaita |
| sub-account | subsąskaita |
| detail / leaf account | detalioji sąskaita |
| journal entry / entry / transaction | įrašas (buhalterinis įrašas) |
| journal entries (tab) | įrašai |
| line (of an entry) | įrašo eilutė |
| journal | žurnalas |
| general ledger | didžioji knyga |
| sub-ledger | pagalbinė knyga |
| trial balance | apyvartų žiniaraštis |
| balance sheet | balansas |
| income statement / profit and loss / P&L | pelno (nuostolių) ataskaita |
| statement of financial position (HK) | finansinės būklės ataskaita |
| statement of profit or loss (HK) | pelno arba nuostolių ataskaita |
| assets / current assets / non-current assets | turtas / trumpalaikis turtas / ilgalaikis turtas |
| liabilities / current / non-current | įsipareigojimai / trumpalaikiai / ilgalaikiai įsipareigojimai |
| equity | nuosavas kapitalas |
| retained earnings | nepaskirstytasis pelnas |
| revenue / income | pajamos / pardavimo pajamos |
| cost of sales / COGS | pardavimo savikaina |
| expenses (account type, P&L) | sąnaudos |
| expenses (expense-claims tab, key `Expenses_tab`) | išlaidų ataskaitos |
| gross profit / operating profit / net income | bendrasis pelnas / veiklos pelnas / grynasis pelnas |
| opening balance | pradinis likutis |
| closing balance | galutinis likutis |
| balance | likutis |
| debit / credit (DR / CR) | debetas / kreditas (D / K) |
| draft | juodraštis |
| post / posted | registruoti / užregistruotas |
| book (an invoice) / booking | kontuoti / kontavimas |
| booking defaults | numatytasis kontavimas |
| booking engine | kontavimo variklis |
| void / voided | anuliuoti / anuliuotas |
| reversal (entry) | storno įrašas |
| accounting period / period | ataskaitinis laikotarpis / laikotarpis |
| fiscal year / FY | finansiniai metai / FM |
| year-end closing | finansinių metų uždarymas |
| year to date (YTD) | nuo metų pradžios |
| close / reopen a period | uždaryti / vėl atidaryti |
| closing checklist | uždarymo kontrolinis sąrašas |
| blocker | kliūtis |
| gap (line awaiting an account) | laukianti eilutė (eilutė be sąskaitos) |
| bank reconciliation | banko suderinimas |
| match / unmatch / matched | suderinti / atšaukti suderinimą / suderinta |
| match group | suderinimo grupė |
| bank statement / bank line | banko išrašas / banko eilutė |
| bank account | banko sąskaita |
| counterparty | kontrahentas |
| accounts payable / receivable | mokėtinos sumos (tiekėjams) / gautinos sumos (iš pirkėjų) |
| AP / AR aging | mokėtinų / gautinų sumų senaties analizė |
| aging bucket / "Current" bucket | senaties intervalas / nepradelsta |
| supplier / vendor | tiekėjas |
| customer | pirkėjas (klientas) |
| invoice / sales invoice / bill (supplier invoice) | sąskaita faktūra / pardavimo sąskaita faktūra / pirkimo sąskaita faktūra |
| receipt | kvitas |
| payment | mokėjimas |
| payment in / out (inbound / outbound) | įplauka / išmoka |
| payer / payee | mokėtojas / gavėjas |
| payment method | mokėjimo būdas |
| bank transfer / check / credit card / cash | banko pavedimas / čekis / kredito kortelė / grynieji pinigai |
| due date | mokėjimo terminas |
| net / tax / gross (total) | be mokesčių (neto) / mokestis / su mokesčiais (bruto) |
| currency | valiuta |
| base currency | bazinė valiuta |
| exchange rate | valiutos kursas |
| exchange difference / gain / loss | valiutos kurso skirtumas / kurso pelnas / kurso nuostolis |
| exchange clearing account | valiutos keitimo tarpinė sąskaita |
| company-specific rate (override) | įmonės kursas |
| categorization rule | priskyrimo taisyklė |
| bank-line rule | banko eilutės taisyklė |
| pattern | atpažinimo šablonas |
| split (across accounts) | paskirstyti / paskirstymas |
| fixed asset | ilgalaikis turtas |
| depreciation / accumulated depreciation | nusidėvėjimas / sukauptas nusidėvėjimas |
| depreciation charge | nusidėvėjimo sąnaudos |
| useful life / salvage value / book value | naudingo tarnavimo laikas / likvidacinė vertė / likutinė vertė |
| straight-line / declining | tiesinis / mažėjančio likučio |
| asset register | ilgalaikio turto registras |
| expense sheet | išlaidų ataskaita |
| reimbursement | išlaidų kompensavimas |
| employee | darbuotojas |
| approve / reject / submit | patvirtinti / atmesti / pateikti |
| VAT | PVM (pridėtinės vertės mokestis) |
| GST / GST-HST / sales tax / consumption tax | prekių ir paslaugų mokestis (GST) / GST-HST / pardavimo mokestis / vartojimo mokestis |
| output VAT / input VAT | pardavimo PVM / pirkimo PVM |
| VAT payable / VAT credit | mokėtinas PVM / PVM permoka |
| credit brought / carried forward | perkelta permoka / į kitą laikotarpį perkeliama permoka |
| surcharge (China) | papildomas mokestis |
| urban construction tax / education surcharge | miesto statybos mokestis / švietimo papildomas mokestis |
| corporate income tax (CIT) | įmonių pelno mokestis |
| individual income tax (IIT) | gyventojų pajamų mokestis (GPM) |
| profits tax (Hong Kong) | pelno mokestis |
| provisional tax | avansinis mokestis |
| prepaid tax (asset) | iš anksto sumokėtas mokestis |
| assessment notice / demand note | mokesčio apskaičiavimo pranešimas / mokėjimo pranešimas |
| tax return / filing | deklaracija |
| accrual entry (tax) | kaupimo įrašas |
| settlement entry (VAT) | užskaitos įrašas |
| settle (a filing) | atsiskaityti |
| add-back / deduction | pridedama suma / atskaitymas |
| tax computation adjustments | mokesčio apskaičiavimo koregavimai |
| assessable profit | apmokestinamasis pelnas |
| losses brought forward | perkelti nuostoliai |
| two-tier / tiered rates | dviejų pakopų tarifas / pakopiniai tarifai |
| tax role mapping / mapped | susiejimas / susieta |
| template | šablonas |
| company | įmonė |
| legal entity name | juridinis pavadinimas |
| registration number / tax ID | įmonės kodas / mokesčių mokėtojo kodas |

## Documents (K4mi)

| English | Lithuanian |
|---|---|
| document | dokumentas |
| tag / K4mi tag | žyma / K4mi žyma |
| custom field | pasirinktinis laukas |
| correspondent | korespondentas |
| document type | dokumento tipas |
| storage path | saugojimo kelias |
| workflow | darbo eiga |
| owner | savininkas |
| archive serial number | archyvo serijos numeris |
| inbox | gautieji |
| saved view | išsaugotas rodinys |
| business card | vizitinė kortelė |
| needs review / mark reviewed | reikia peržiūrėti / pažymėti kaip peržiūrėtą |
| extraction / extract | duomenų išgavimas / išgauti |
| reprocess | apdoroti iš naujo |
| confidence | patikimumas |

## UI words (Open WebUI's Lithuanian file, corrected where it is wrong)

| English | Lithuanian |
|---|---|
| settings | nustatymai |
| dashboard | suvestinė |
| save | išsaugoti |
| cancel | atšaukti |
| delete | ištrinti |
| edit | redaguoti |
| search | ieškoti / paieška |
| filter | filtruoti / filtras |
| export / import | eksportuoti / importuoti |
| upload / download | įkelti / atsisiųsti |
| apply | taikyti |
| confirm | patvirtinti |
| create / add / remove | sukurti / pridėti / pašalinti |
| close | uždaryti |
| refresh / reset / clear | atnaujinti / atkurti / išvalyti |
| select | pasirinkti |
| loading… | įkeliama… |
| error / warning | klaida / įspėjimas |
| status | būsena |
| permissions / group | teisės / grupė |
| preview | peržiūra |
| details | išsami informacija |
| report | ataskaita |
| user | naudotojas |
| language | kalba |
| enabled / disabled | įjungta / išjungta |
| optional / required | neprivaloma / privaloma |
