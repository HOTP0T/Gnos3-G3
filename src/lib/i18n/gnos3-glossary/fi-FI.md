# Gnos3 business modules — Finnish (fi-FI) glossary

Translators of Gnos3, Finances, K4mi, Open WebUI and the expense app follow this list.

## Conventions

- **Register**: neutral, professional Finnish as in Finnish business software. Buttons and menu items use the singular imperative ("Tallenna", "Kirjaa", "Lähetä hyväksyttäväksi"). Messages prefer the passive or a neutral statement ("Tiliä ei löytynyt", "Kirjaus tallennettiin"); when the user must be addressed, use the singular "sinä" form as Open WebUI's Finnish file does ("Haluatko varmasti poistaa…?"). Never "Te".
- **Case**: sentence case for everything (headings, buttons, tabs). Abbreviations in capitals: ALV, D / K, Tk, PDF, CSV.
- **Placeholders** (`{{name}}`, `{code}`) cannot take Finnish case endings. Keep them in the nominative by putting a head noun before them ("tili {code}", "yritys {{name}}"), or by using a colon form only for codes/numbers where natural ("{{count}} kpl"). Never glue an ending to a placeholder.
- **Punctuation**: Finnish quotation marks ”…” (the same closing-style mark on both sides) around UI labels and names; en dash with spaces " – " for a parenthetical dash; no space before ":" "?" "!"; ellipsis "…". "e.g." = "esim.", "i.e." = "eli", "etc." = "jne.", "approx." = "n.".
- **Numbers and dates**: decimal comma, (non-breaking) space as thousands separator (1 234,56 €); dates d.m.yyyy (31.12.2026); months lowercase (tammikuu, joulukuu); percent with a space ("24 %").
- **Compounds**: Finnish writes compounds as one word ("pankkitili", "tilikarttapohja"); with an abbreviation or a product name use a hyphen ("ALV-ilmoitus", "K4mi-tunniste", "Excel-tiedosto", "PDF-tiedosto").
- **Upload / download**: upload = "lähettää" ("Lähetä"), download = "ladata" ("Lataa") — never "Lataa" for upload, so the two never read the same.
- **Statement totals** written in capitals in the source stay in capitals.
- **Expenses**: as an account type / P&L line / dashboard figure = "kulut"; the expense-claims tab or settings group (key `Expenses_tab`) = "kuluraportit".

## Accounting and finance

| English | Finnish |
|---|---|
| account (ledger) | tili |
| account name / code | tilin nimi / tilinumero |
| account type | tilityyppi |
| chart of accounts | tilikartta |
| chart template | tilikarttapohja |
| control account (with sub-accounts) | kokoomatili |
| sub-account | alatili |
| detail / leaf account | alimman tason tili |
| journal entry / entry / transaction | kirjaus |
| entry line | kirjausrivi (vienti) |
| voucher (manual) | tosite (muistiotosite) |
| journal | päiväkirja |
| general ledger | pääkirja |
| sub-ledger | reskontra |
| trial balance | koetase |
| balance sheet | tase |
| income statement / P&L / profit and loss | tuloslaskelma |
| statement of financial position (HK) | taloudellista asemaa kuvaava laskelma |
| statement of profit or loss (HK) | tuloslaskelma |
| assets / liabilities | varat / velat |
| current / non-current assets | lyhytaikaiset / pitkäaikaiset varat |
| current / non-current liabilities | lyhytaikaiset / pitkäaikaiset velat |
| equity | oma pääoma |
| retained earnings | kertyneet voittovarat |
| revenue | tuotot (on statements: liikevaihto) |
| cost of sales / COGS | myytyjen suoritteiden kulut |
| gross profit | myyntikate |
| operating profit | liikevoitto |
| net income / profit for the year | tilikauden tulos |
| opening balance | alkusaldo |
| closing balance | loppusaldo |
| debit / credit (DR / CR) | debet / kredit (D / K) |
| draft | luonnos |
| post / posted | kirjata / kirjattu ("Kirjaa") |
| book an invoice / booking | tiliöidä / tiliöinti |
| booking defaults | tiliöinnin oletukset |
| booking engine | tiliöintimoottori |
| void / voided | mitätöidä / mitätöity ("Mitätöi kirjaus") |
| reversal (entry) | vastakirjaus |
| accounting period / period | kirjanpitojakso / jakso |
| fiscal year / FY | tilikausi / Tk |
| year to date (YTD) | tilikauden alusta (kertymä) |
| year-end close | tilikauden päättäminen |
| close / reopen a period | sulje / avaa uudelleen |
| closing checklist | päättämisen tarkistuslista |
| blocker | este |
| gap (line awaiting an account) | avoin rivi (odottaa tiliä) |
| bank reconciliation | pankkitäsmäytys |
| match / unmatch / matched | täsmäytä / poista täsmäytys / täsmäytetty |
| match group | täsmäytysryhmä |
| bank statement | tiliote |
| bank line | tilioterivi |
| bank account | pankkitili |
| counterparty | vastapuoli |
| accounts payable / receivable (AP / AR) | ostovelat / myyntisaamiset |
| AP / AR aging | ostovelkojen / myyntisaamisten ikäjakauma |
| aging bucket / "Current" bucket | ikäluokka / erääntymätön |
| supplier / vendor | toimittaja |
| customer / client | asiakas |
| bill (supplier invoice) | ostolasku |
| sales invoice | myyntilasku |
| invoice | lasku |
| receipt | kuitti |
| payment | maksu |
| payment in / out | saapuva / lähtevä maksu |
| payer / payee | maksaja / saaja |
| payment method | maksutapa |
| bank transfer / check / credit card / cash | tilisiirto / sekki / luottokortti / käteinen |
| due date | eräpäivä |
| currency / base currency | valuutta / perusvaluutta |
| exchange rate | valuuttakurssi (kurssi) |
| exchange difference / gain / loss | kurssiero / kurssivoitto / kurssitappio |
| exchange clearing account | valuuttojen välitili |
| company-specific rate (override) | yrityskohtainen kurssi |
| categorization rule | tiliöintisääntö |
| bank-line rule | tilioterivisääntö |
| category (expense) | kululuokka |
| pattern (to match) | hakuehto |
| split (across accounts) | jakaa / jako |
| fixed asset | käyttöomaisuushyödyke (käyttöomaisuus) |
| depreciation / accumulated depreciation | poisto / kertyneet poistot |
| useful life / salvage value / book value | taloudellinen vaikutusaika / jäännösarvo / kirjanpitoarvo |
| straight-line / declining balance | tasapoisto / menojäännöspoisto |
| asset register | käyttöomaisuusrekisteri |
| expense sheet / expense claim | kuluraportti |
| reimbursement | kulukorvaus |
| employee | työntekijä |
| approve / reject / submit | hyväksy / hylkää / lähetä hyväksyttäväksi |
| VAT | ALV (arvonlisävero) |
| GST / GST-HST / sales tax / consumption tax | GST / GST-HST / myyntivero / kulutusvero |
| output / input VAT | myynnin ALV / ostojen ALV |
| VAT payable / VAT credit | maksettava ALV / ALV-saaminen |
| credit brought / carried forward | edelliseltä kaudelta siirtynyt / seuraavalle kaudelle siirtyvä saaminen |
| VAT settlement entry | ALV-tilityskirjaus |
| surcharge (China, on VAT) | lisävero |
| corporate income tax (CIT) | yhteisövero |
| individual income tax (IIT) | henkilön tulovero |
| withholding | ennakonpidätys |
| profits tax (Hong Kong) | voittovero |
| provisional tax | ennakkovero |
| prepaid tax (asset) | maksettu ennakkovero |
| assessment notice / demand note | verotuspäätös / maksukehotus |
| tax return / filing | veroilmoitus |
| accrual entry | jaksotuskirjaus |
| settle (a tax filing) | tilitä |
| add-back / deduction | lisäys / vähennys |
| tax computation adjustments | verotuksen oikaisut |
| assessable profit | verotettava tulo |
| losses brought forward | aiempien vuosien tappiot |
| two-tier / tiered rates | kaksiportainen / porrastettu verokanta |
| tax role mapping / mapped | verotilien määritys / määritetty |
| template | pohja |
| company | yritys |
| legal entity name | virallinen nimi |
| business card | käyntikortti |
| needs review / mark reviewed | tarkistettava / merkitse tarkistetuksi |
| books language | kirjanpidon kieli |

## Documents (K4mi)

| English | Finnish |
|---|---|
| document | asiakirja |
| tag / K4mi tag | tunniste / K4mi-tunniste |
| custom field | mukautettu kenttä |
| correspondent | yhteyshenkilö |
| document type | asiakirjatyyppi |
| storage path | tallennustilan polku |
| workflow | työnkulku |
| archive serial number | arkistointisarjanumero |
| upload | lähetä (lähettää) |
| reprocess | käsittele uudelleen |
| extraction | tietojen poiminta |
| confidence | luotettavuus |

## Interface words

| English | Finnish |
|---|---|
| settings | asetukset |
| dashboard | koontinäyttö |
| save | tallenna |
| cancel | peruuta |
| delete / remove | poista |
| edit | muokkaa |
| search | hae (noun: haku) |
| filter | suodata (noun: suodatin) |
| export / import | vie / tuo |
| download | lataa |
| apply | käytä (apply changes: ota käyttöön) |
| confirm | vahvista |
| loading… | ladataan… |
| error / warning | virhe / varoitus |
| close | sulje |
| create / add | luo / lisää |
| status | tila |
| permissions | käyttöoikeudet |
| group / user / role | ryhmä / käyttäjä / rooli |
| preview | esikatselu |
| optional / required | valinnainen / pakollinen |
| enabled / disabled | käytössä / ei käytössä |
| AI | tekoäly |
| anonymise / Anonymiser (module) | anonymisoi / Anonymisointi |
| Finances (module) | Talous |
| SmartOffice, K4mi, Gnos3 | unchanged; a name ending in a digit takes a colon before the case ending (K4mi:ssa, K4mi:stä, Gnos3:n), others inflect normally (SmartOfficessa) |
| trip (expense app) | matka |
| merchant | kauppias |
