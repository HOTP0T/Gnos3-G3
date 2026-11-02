# Gnos3 — Bosanski (latinica) glossary (bs-BA)

## Conventions

- **Standard**: Bosnian, Latin script, ijekavian (vrijednost, primijeniti, mjesec, izvještaj, uspjeh). Prefer the Bosnian word where Bosnian and Croatian differ: preduzeće (not poduzeće), kurs (not tečaj), historija (not povijest), sedmica (not tjedan), hiljada (not tisuća), kolona (not stupac), tabela (not tablica), tačka / tačno (not točka / točno), primalac / platilac (not primatelj / platitelj), lični (not osobni), šablon (not predložak), uslov (not uvjet), finansijski (not financijski).
- **Form of address**: polite plural "vi", lowercase, as the existing Open WebUI catalog does ("Unesite naziv", "Vaši podaci", "Odaberite preduzeće"). Never "ti" in sentences.
- **Buttons and menu items**: short imperative, 2nd person singular, as the existing catalog does (Spremi, Otkaži, Izbriši, Uredi, Dodaj, Potvrdi, Primijeni, Proknjiži, Storniraj). Column headers and labels are nouns (Datum, Iznos, Konto).
- **Case**: sentence case — only the first word and proper names capitalised (Glavna knjiga, Bruto bilans, not "Glavna Knjiga"). Month and weekday names are lowercase (januar, ponedjeljak). ALL-CAPS statement totals stay in capitals.
- **Punctuation**: no space before ":" "?" "!"; quotation marks „…“ around quoted UI labels and names; "npr." for "e.g.", "tj." for "i.e.", "itd." for "etc."; an ellipsis "…" (or "...") as in the source.
- **Numbers and dates**: decimal comma and dot as thousands separator (1.234,56); dates dd.mm.yyyy. (31.12.2026.); amounts with the currency after the number (1.234,56 KM / BAM). Formatting itself is done in code — only write numbers in prose this way.
- **Months**: januar, februar, mart, april, maj, juni, juli, august, septembar, oktobar, novembar, decembar.
- **DR / CR**: Dug. / Pot. (duguje / potražuje).
- **Grammar with placeholders**: when a `{{count}}` / `{count}` precedes a noun, use a neutral form that reads for any number where possible ("Stavki: {{count}}", "{{count}} stavka/stavki") rather than a wrong plural.
- **Tax names in placeholders** (`{{tax}}` / `{tax}` = PDV, GST…): put the name where its case does not matter ("Prijava – {{tax}}", "{{tax}}: obaveza"), since PDV is used undeclined in many places.
- **Product names** stay as they are: Gnos3, K4mi, SmartOffice, Ollama, Open WebUI, Excel, PDF, CSV, currency codes, units.

## Terms

| English | Bosanski |
|---|---|
| account (ledger) | konto |
| accounts (ledger) | konta |
| account code / account name | šifra konta / naziv konta |
| chart of accounts | kontni plan |
| control account (has sub-accounts) | sintetički konto |
| sub-account | podkonto |
| detail / leaf account | analitički konto |
| account type | vrsta konta |
| journal entry / entry / transaction | knjiženje (pl. knjiženja) |
| entry line | stavka knjiženja |
| journal | dnevnik |
| general ledger | glavna knjiga |
| sub-ledger | pomoćna knjiga |
| trial balance | bruto bilans |
| balance sheet | bilans stanja |
| profit and loss / income statement | bilans uspjeha |
| statement of financial position (HK) | izvještaj o finansijskom položaju |
| statement of profit or loss (HK) | izvještaj o dobiti ili gubitku |
| current / non-current assets | tekuća / stalna sredstva |
| current / non-current liabilities | kratkoročne / dugoročne obaveze |
| assets / liabilities / equity | sredstva (imovina) / obaveze / kapital |
| revenue / income | prihodi |
| expenses (account type, P&L) | rashodi |
| expenses (expense-claims tab, `Expenses_tab`) | obračuni troškova |
| cost of sales | troškovi prodaje (nabavna vrijednost prodatog) |
| retained earnings | zadržana dobit |
| opening balance | početno stanje |
| closing balance | završno stanje |
| balance (of an account) | saldo |
| debit / credit | duguje / potražuje (Dug. / Pot.) |
| draft | nacrt |
| post / posted | proknjiži / proknjiženo |
| book (an invoice) / booking | knjiži / knjiženje |
| booking defaults | zadane postavke knjiženja |
| void / voided | storniraj / stornirano |
| reversal (entry) | storno knjiženje |
| accounting period / period | obračunski period / period |
| fiscal year (FY) | poslovna godina (PG) |
| year to date (YTD) | od početka godine |
| year-end closing | zaključenje poslovne godine |
| close / reopen (a period) | zaključi / ponovo otvori |
| closing checklist | kontrolna lista zaključenja |
| blocker | prepreka |
| gap (line awaiting an account) | stavka na čekanju |
| bank reconciliation | bankovno usaglašavanje |
| reconcile / reconciled | usaglasi / usaglašeno |
| match / unmatch / matched | upari / poništi uparivanje / upareno |
| match group | grupa uparivanja |
| bank statement | bankovni izvod |
| bank line (statement line) | stavka izvoda |
| bank account | bankovni račun |
| counterparty | partner |
| counterparty account (AP/AR) | konto partnera |
| accounts payable / receivable | obaveze prema dobavljačima / potraživanja od kupaca |
| AP / AR aging | starosna struktura obaveza / potraživanja |
| "Current" aging bucket | nedospjelo |
| supplier / vendor | dobavljač |
| customer / client | kupac |
| invoice | faktura |
| bill (supplier invoice) / sales invoice | ulazna faktura / izlazna faktura |
| receipt (expense proof) | račun (dokaz o trošku) |
| payment | plaćanje |
| payment in / out | uplata / isplata |
| payer / payee | platilac / primalac |
| payment method | način plaćanja |
| bank transfer / cheque / card / cash | bankovni transfer / ček / kartica / gotovina |
| due date | datum dospijeća |
| currency | valuta |
| base currency | osnovna valuta |
| exchange rate | kurs |
| exchange difference / gain / loss | kursna razlika / pozitivna kursna razlika / negativna kursna razlika |
| exchange clearing account | prelazni konto za konverziju |
| rate override (company) | posebni kurs |
| categorization rule | pravilo kategorizacije |
| bank-line rule | pravilo za stavke izvoda |
| pattern | uzorak |
| split (across accounts) | raspodijeli / raspodjela |
| fixed asset | osnovno sredstvo |
| depreciation / accumulated depreciation | amortizacija / akumulirana amortizacija |
| useful life / salvage value / book value | korisni vijek / ostatak vrijednosti / knjigovodstvena vrijednost |
| expense sheet | obračun troškova |
| reimbursement | refundacija |
| employee | zaposlenik |
| approve / reject / submit | odobri / odbij / podnesi |
| VAT | PDV (porez na dodanu vrijednost) |
| output VAT / input VAT | izlazni PDV / ulazni PDV |
| VAT payable / VAT credit | PDV obaveza / PDV kredit |
| credit brought / carried forward | preneseni kredit / kredit za prijenos |
| GST / sales tax / consumption tax | GST (porez na robu i usluge) / porez na promet / porez na potrošnju |
| surcharge (on VAT, China) | prirez |
| corporate income tax (CIT) | porez na dobit |
| profits tax (Hong Kong) | porez na dobit (Hong Kong) |
| individual income tax (IIT) | porez na dohodak |
| provisional tax | akontacija poreza |
| prepaid tax | unaprijed plaćeni porez |
| assessment notice / demand note | porezno rješenje / poziv za plaćanje akontacije |
| tax return / filing | porezna prijava / prijava |
| accrual entry (tax) | knjiženje obračuna |
| settlement entry (VAT) | knjiženje zatvaranja |
| settle | izmiri |
| add-back / deduction | uvećanje / umanjenje (porezne osnovice) |
| tax adjustments | porezne korekcije |
| assessable profit | oporeziva dobit |
| losses brought forward | preneseni gubici |
| tiered rates | stope po razredima |
| tax role mapping / mapped | povezivanje / povezano |
| template | šablon |
| company | preduzeće |
| legal entity name | puni naziv pravnog lica |
| business card | vizit karta |
| needs review / mark reviewed | za provjeru / označi kao provjereno |
| confidence (extraction) | pouzdanost |
| document | dokument |
| tag | oznaka |
| custom field | prilagođeno polje |
| correspondent | dopisnik |
| document type | vrsta dokumenta |
| storage path | putanja pohrane |
| workflow | tok rada |
| upload | učitaj (noun: učitavanje) |
| download | preuzmi (noun: preuzimanje) |
| file | datoteka |
| settings | postavke |
| dashboard | nadzorna ploča |
| save | spremi |
| cancel | otkaži |
| delete | izbriši |
| remove | ukloni |
| edit | uredi |
| create / add | kreiraj / dodaj |
| search | pretraga (button: pretraži) |
| filter | filter (verb: filtriraj) |
| export / import | izvoz / uvoz (buttons: izvezi / uvezi) |
| apply | primijeni |
| confirm | potvrdi |
| close (dialog) | zatvori |
| loading… | učitavanje… |
| error / warning | greška / upozorenje |
| status | status |
| pending | na čekanju |
| group / role / permission | grupa / uloga / dozvola |
| user / admin / superadmin | korisnik / administrator / superadministrator |
| anonymise / personal details | anonimiziraj / lični podaci |
