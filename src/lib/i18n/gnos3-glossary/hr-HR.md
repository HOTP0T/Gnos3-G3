# Gnos3 — Croatian (hr-HR) glossary

For every Croatian translator of Gnos3, Finances, K4mi, Open WebUI and the expense app. Accounting words follow Croatian practice (Zakon o računovodstvu, HSFI / MSFI, Zakon o PDV-u); UI words follow Open WebUI's existing `hr-HR/translation.json` and K4mi's `messages.hr_HR.xlf` where those already have them.

## Conventions

- **Register**: formal and impersonal. Instructions and messages address the reader in the polite plural, lowercase: „Odaberite tvrtku“, „Unesite iznos“, „vaš račun“ (no courtesy capital „Vi/Vaš“ in UI text).
- **Buttons and menu items**: short imperative singular, as Croatian software does: „Spremi“, „Odustani“, „Izbriši“, „Proknjiži“, „Dodaj konto“. Tabs and headings are nouns: „Postavke“, „Plaćanja“, „Izvješća“.
- **Case**: sentence case („Bruto bilanca“, „Uvoz kontnog plana“). ALL-CAPS totals in statements stay in capitals.
- **Punctuation**: Croatian quotation marks „…“ for quoted labels; ellipsis „…“ for running actions („Učitavanje…“, „Spremanje…“); no space before „:“ „?“ „!“; em dash with spaces „ — “ as in the source.
- **Abbreviations**: „npr.“ for „e.g.“, „tj.“ for „i.e.“, „br.“ for „No.“; D / P (duguje / potražuje) for DR / CR; „PDV“ for VAT (declines: PDV-a, PDV-u).
- **Numbers and dates**: decimal comma, thousands separated by a dot (1.234,56); dates „dd. mm. gggg.“ (30. 10. 2026.); currency codes after the amount (1.234,56 EUR). The app formats numbers itself — never hard-code a format in a string.
- **Placeholders**: keep `{{name}}` / `{name}` / `<0>` exactly. Croatian declines nouns: rephrase so the placeholder sits in the nominative where possible („Tvrtka: {{name}}“, „Konto {code} nije pronađen“).
- **Plurals**: Croatian has three forms (1 / 2–4 / 5+). Where the source has only one/other, use the form that reads for most counts, or a neutral wording („Broj stavki: {{count}}“).
- **Product names** stay as they are: Gnos3, K4mi, SmartOffice, Ollama, Open WebUI, Excel, PDF, CSV, currency codes.

## Terms

| English | Croatian |
|---|---|
| account (ledger account) | konto |
| account name / code | naziv konta / šifra konta |
| account type | vrsta konta |
| chart of accounts | kontni plan |
| control account (with sub-accounts) | sintetički konto |
| sub-account / detail (leaf) account | analitički konto |
| journal entry / entry / transaction | knjiženje (temeljnica for a voucher) |
| entry line | stavka knjiženja |
| journal | dnevnik |
| general ledger | glavna knjiga |
| sub-ledger | pomoćna knjiga |
| trial balance | bruto bilanca |
| balance sheet | bilanca |
| profit and loss / income statement | račun dobiti i gubitka (RDG) |
| statement of financial position | izvještaj o financijskom položaju |
| statement of profit or loss | izvještaj o dobiti ili gubitku |
| assets / current / non-current | imovina / kratkotrajna / dugotrajna |
| liabilities / current / non-current | obveze / kratkoročne / dugoročne |
| equity | kapital |
| retained earnings | zadržana dobit |
| revenue / income | prihodi |
| expense (account type, P&L) | rashodi |
| cost of sales | trošak prodanog |
| fiscal year | poslovna godina |
| year to date (YTD) | od početka godine (kumulativno) |
| accounting period / period | obračunsko razdoblje / razdoblje |
| year-end closing | zaključenje poslovne godine |
| close / reopen a period | zaključiti / ponovno otvoriti |
| closing checklist | kontrolni popis za zaključenje |
| opening balance | početno stanje |
| closing balance | završno stanje |
| debit / credit | duguje / potražuje (D / P) |
| balance | saldo |
| draft | nacrt |
| post / posted | proknjižiti / proknjiženo |
| void / voided | stornirati / stornirano |
| reversal | storno knjiženje |
| book (an invoice) / booking | knjižiti / knjiženje |
| booking defaults | zadana knjiženja |
| gap (line awaiting an account) | nedostaje konto / otvorena stavka |
| blocker | prepreka |
| VAT | PDV (porez na dodanu vrijednost) |
| GST / sales tax / consumption tax | GST / porez na promet / porez na potrošnju |
| output VAT / input VAT | izlazni PDV / pretporez |
| VAT payable / VAT credit | obveza za PDV / preplata PDV-a |
| VAT return | prijava PDV-a |
| corporate income tax (CIT) | porez na dobit |
| profits tax (Hong Kong) | porez na dobit (Profits Tax) |
| individual income tax (IIT) | porez na dohodak |
| provisional tax / prepaid tax | predujam poreza / plaćeni predujam |
| assessment notice / demand note | rješenje o razrezu / poziv na plaćanje |
| tax return / filing | porezna prijava |
| accrual entry | knjiženje razgraničenja (obračuna) poreza |
| settle / settlement entry | podmiriti / knjiženje podmirenja |
| add-back / deduction | uvećanje / umanjenje porezne osnovice |
| assessable profit | porezna osnovica |
| losses brought forward | preneseni porezni gubici |
| tax role mapping | povezivanje poreznih uloga s kontima |
| surcharge | prirez / dodatni porez |
| invoice | račun |
| sales invoice / supplier invoice (bill) | izlazni račun / ulazni račun |
| receipt (expense proof) | račun (potvrda o plaćanju) |
| payment / payment in / payment out | plaćanje / uplata / isplata |
| payer / payee | platitelj / primatelj plaćanja |
| payment method | način plaćanja |
| bank transfer / card / cash | bankovni prijenos / kartica / gotovina |
| bank account | bankovni račun |
| bank statement | bankovni izvod |
| bank line | stavka izvoda |
| bank reconciliation | usklađivanje s izvodom |
| match / unmatch / matched | upariti / poništiti uparivanje / upareno |
| match group | grupa uparivanja |
| counterparty | druga strana |
| supplier / vendor | dobavljač |
| customer / client | kupac |
| accounts payable / receivable | obveze prema dobavljačima / potraživanja od kupaca |
| AP / AR aging | starosna struktura obveza / potraživanja |
| expense (claim) | trošak |
| expense sheet | obračun troškova |
| reimbursement | povrat troškova |
| employee | zaposlenik |
| approve / reject / submit | odobriti / odbiti / predati |
| company | tvrtka |
| legal entity name | naziv pravne osobe |
| currency / base currency | valuta / osnovna valuta |
| exchange rate | tečaj |
| exchange difference / gain / loss | tečajna razlika / pozitivna / negativna tečajna razlika |
| exchange clearing account | prijelazni konto za tečajne razlike |
| fixed asset | dugotrajna imovina (osnovno sredstvo) |
| depreciation / accumulated depreciation | amortizacija / ispravak vrijednosti |
| useful life / salvage value / book value | vijek uporabe / ostatak vrijednosti / knjigovodstvena vrijednost |
| categorization rule | pravilo kategorizacije |
| pattern | uzorak |
| split | raspodjela / raspodijeliti |
| template | predložak |
| business card | posjetnica |
| needs review / reviewed | potrebna provjera / provjereno |
| document | dokument |
| tag | oznaka |
| custom field | prilagođeno polje |
| correspondent | dopisnik |
| document type | vrsta dokumenta |
| storage path | putanja pohrane |
| archive serial number | serijski broj pohrane |
| workflow | tijek rada |
| inbox | ulazni spremnik |
| owner | vlasnik |
| permissions | dopuštenja |
| group / user | grupa / korisnik |
| dashboard | nadzorna ploča |
| settings | postavke |
| save | spremi |
| cancel | odustani |
| delete | izbriši |
| edit | uredi |
| search | pretraži / pretraga |
| filter | filtriraj / filtar |
| export / import | izvezi / uvezi (nouns: izvoz / uvoz) |
| upload | učitaj (noun: učitavanje) |
| download | preuzmi |
| apply | primijeni |
| confirm | potvrdi |
| create / add / remove | stvori / dodaj / ukloni |
| refresh / reset | osvježi / vrati na zadano |
| loading… | učitavanje… |
| saving… | spremanje… |
| error / warning | greška / upozorenje |
| status | status |
| amount / total | iznos / ukupno |
| description / reference | opis / poziv na broj (bank) / oznaka (entry reference) |
| knowledge base | baza znanja |
| anonymise | anonimizirati |
