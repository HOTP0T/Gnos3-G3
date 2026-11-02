# Gnos3 — Norwegian Bokmål (nb-NO) glossary

## Conventions

- **Form of address**: "du" (the normal register of Norwegian business software: Tripletex, Fiken, PowerOffice, Microsoft). Never "De". Polite but direct: "Velg en konto", "Dette kan ikke angres."
- **Buttons**: imperative, short, sentence case: "Lagre", "Opprett postering", "Bokfør", "Eksporter til Excel", "Last opp". No accent on imperatives (Eksporter, Importer, Rediger).
- **Sentence case**: only the first word and proper names take a capital. Month and weekday names, languages and nationality adjectives are lower case (januar, mandag, norsk).
- **Compounds are one word** (mva-melding, bankavstemming, kontoplan, regnskapsår). After an abbreviation, a product name, a number or a placeholder use a hyphen: K4mi-etikett, PDF-fil, CSV-fil, Excel-fil, KI-forslag, MPF-innskudd, mva-kode, {{name}}-mal.
- **AI** = "KI" (kunstig intelligens) in running text and labels: "KI-forslag", "Kategoriser (KI)". Model and product names stay as they are (Ollama, Open WebUI).
- **Punctuation**: no space before ":" "?" "!". Quoted UI labels and names in «…» («{{name}}» fjernes). Ellipsis as "…". "e.g." = "f.eks.", "i.e." = "dvs.", "etc." = "osv.", "approx." = "ca.", "incl." = "inkl.", "excl." = "ekskl.". Em dashes are kept where the English uses them, with spaces ( — ).
- **Numbers and dates** (in examples / text): decimal comma, space as thousands separator (1 234,56); currency code before or after as the screen shows it (NOK 1 234,56 / 1 234,56 kr); dates dd.mm.åååå or "31. mars 2026"; percent with a space: "25 %".
- **Debit / credit** columns: "Debet" / "Kredit"; abbreviations DR / CR → D / K.
- **Statement totals** written in ALL CAPS in the source stay in capitals (EIENDELER, SUM GJELD).
- **Tax placeholders**: UI `{{tax}}` / books `{tax}` is filled with a capitalised term ("Mva", "GST", "Forbruksavgift"); put it first or after a colon / parenthesis when natural ("{{tax}} å betale", "Melding: {{tax}}"); otherwise accept it mid-sentence ("Utgående {{tax}}"). `{{cit}}` is "Selskapsskatt" / "Overskuddsskatt".
- **mva** is written in lower case in running text ("utgående mva", "mva-melding"), "Mva" at the start of a label.
- **Account (Open WebUI)** = the user's profile/login ("Konto" in Open WebUI's file); **Account_gnos3** = a ledger account ("Konto"). Plural of konto: "kontoer", definite "kontoene".

## Accounting and finance

| English | Norwegian Bokmål |
|---|---|
| account (ledger) | konto (pl. kontoer) |
| account name / account code | kontonavn / kontonummer |
| account type | kontotype |
| chart of accounts | kontoplan |
| control account (with sub-accounts) | samlekonto |
| sub-account | underkonto |
| detail / leaf account | posteringskonto |
| journal entry / entry / transaction | postering |
| entry line | posteringslinje |
| voucher / manual voucher | bilag / manuelt bilag |
| journal | journal |
| general ledger | hovedbok |
| sub-ledger | reskontro |
| trial balance | saldobalanse |
| balance sheet | balanse |
| income statement / P&L / profit and loss | resultatregnskap |
| statement of financial position (HK) | oppstilling av finansiell stilling |
| statement of profit or loss (HK) | resultatoppstilling |
| assets / liabilities | eiendeler / gjeld (forpliktelser) |
| current / non-current assets | omløpsmidler / anleggsmidler |
| current / non-current liabilities | kortsiktig gjeld / langsiktig gjeld |
| equity | egenkapital |
| retained earnings | opptjent egenkapital |
| revenue / income | driftsinntekter / inntekter |
| cost of sales / COGS | varekostnad |
| gross profit | bruttofortjeneste |
| operating profit | driftsresultat |
| net income / profit for the year | årsresultat |
| administrative expenses | administrasjonskostnader |
| financial expenses / finance costs | finanskostnader |
| expenses (account type, P&L, dashboards) | kostnader |
| opening balance | inngående balanse (IB) |
| closing balance | utgående balanse (UB) |
| balance (of an account) | saldo |
| debit / credit | debet / kredit |
| draft | utkast |
| post / posted | bokføre / bokført |
| book (an invoice), booking | kontere, kontering |
| booking defaults | standardkonteringer |
| booking engine | konteringsmotor |
| gap (line awaiting an account) | manglende kontering |
| void / voided | annullere / annullert ("Void" button = "Annuller postering", never bare "Avbryt" = Cancel) |
| reversal / reverse | reversering / reversere |
| accounting period | regnskapsperiode |
| fiscal year / FY | regnskapsår |
| year to date (YTD) | hittil i år (HiÅ) |
| year-end closing | årsavslutning |
| close / reopen (a period) | lukke / gjenåpne |
| closing checklist | avslutningssjekkliste |
| blocker | blokkerende punkt |
| bank reconciliation | bankavstemming |
| match / unmatch / matched | avstemme / oppheve avstemming / avstemt |
| match group | avstemmingsgruppe |
| auto-match | automatisk avstemming |
| bank statement / bank line | kontoutskrift / banklinje |
| bank account | bankkonto |
| counterparty | motpart |
| accounts payable (AP) | leverandørgjeld (leverandørreskontro) |
| accounts receivable (AR) | kundefordringer (kundereskontro) |
| AP / AR aging | aldersfordelt leverandør- / kundereskontro |
| aging bucket / "Current" bucket | aldersintervall / ikke forfalt |
| supplier / vendor | leverandør |
| customer / client | kunde |
| bill (supplier invoice) | inngående faktura (leverandørfaktura) |
| sales invoice | utgående faktura (salgsfaktura) |
| invoice | faktura (pl. fakturaer) |
| receipt | kvittering |
| payment | betaling |
| payment in / out | innbetaling / utbetaling |
| payer / payee | betaler / betalingsmottaker |
| payment method | betalingsmåte |
| bank transfer / check / credit card / cash | bankoverføring / sjekk / kredittkort / kontant |
| due date | forfallsdato |
| amount | beløp |
| company | selskap (pl. selskaper) |
| legal entity name | juridisk navn |
| currency / base currency | valuta / basisvaluta |
| exchange rate | valutakurs |
| exchange difference / gain / loss | kursdifferanse / kursgevinst (agio) / kurstap (disagio) |
| exchange clearing account | mellomregningskonto for valuta |
| rate override (company rate) | selskapsspesifikk kurs |
| categorization rule | kategoriseringsregel |
| bank-line rule | banklinjeregel |
| pattern | mønster |
| split (across accounts) | fordele, fordeling |
| template | mal |
| fixed asset | anleggsmiddel |
| depreciation / accumulated depreciation | avskrivning / akkumulerte avskrivninger |
| useful life / salvage value / book value | levetid / restverdi / bokført verdi |
| straight-line / declining balance | lineær / saldoavskrivning |
| asset register | anleggsregister |
| expense sheet | utleggsrapport |
| expenses (the expense-claims tab, `Expenses_tab`) | utlegg |
| reimbursement | refusjon |
| employee | ansatt |
| approve / reject / submit | godkjenne / avvise / sende inn |
| VAT | mva (merverdiavgift) |
| tax (amount / rate on an invoice, generic) | avgift (avgiftsbeløp, avgiftssats, inkl. avgift) |
| Tax tab (`Tax_tab`) | Skatt |
| GST / GST/HST / consumption tax / sales tax / ICMS | GST / GST/HST / forbruksavgift / omsetningsavgift / ICMS |
| output / input VAT | utgående mva / inngående mva |
| VAT payable / VAT credit | skyldig mva / mva til gode |
| credit brought forward / carried forward | overført tilgodebeløp / tilgodebeløp til fremføring |
| VAT surcharge (China) | tilleggsavgift |
| corporate income tax (CIT) | selskapsskatt |
| individual income tax (IIT) | personlig inntektsskatt |
| profits tax (Hong Kong) | overskuddsskatt (Profits Tax) |
| provisional tax | forskuddsskatt |
| prepaid tax (asset) | forskuddsbetalt skatt |
| assessment notice / demand note | skatteoppgjør / betalingskrav |
| tax return / filing | melding (mva-melding, skattemelding) |
| accrual entry (tax) | avsetningspostering |
| settlement entry (VAT) | oppgjørspostering |
| settle | gjøre opp |
| add-back / deduction | tillegg / fradrag |
| tax computation adjustments | skattemessige justeringer |
| assessable profit | skattepliktig inntekt |
| losses brought forward | fremførbart underskudd |
| two-tier / tiered rates | totrinnssats / trinnvise satser |
| tax role mapping / mapped | tilordning / tilordnet |
| MPF (HK pension) | MPF (pensjonsinnskudd) |

## Documents (K4mi) and modules

| English | Norwegian Bokmål |
|---|---|
| document | dokument |
| tag (K4mi) | etikett (K4mi-etikett), as in K4mi's catalog |
| custom field | egendefinert felt |
| correspondent | korrespondent |
| document type | dokumenttype |
| storage path | lagringssti |
| archive serial number | arkivserienummer |
| inbox | innboks |
| owner | eier |
| workflow | arbeidsprosess (K4mi's word) |
| webhook | webhook |
| OCR | OCR |
| extraction / extract | uttrekk / trekke ut |
| reprocess | behandle på nytt |
| business card | visittkort |
| needs review / mark reviewed | må gjennomgås / merk som gjennomgått |
| confidence | sikkerhet |
| anonymise (button) / the Anonymiser module | Anonymiser / Anonymisering (module and page name) |
| labels mode ([PERSON_1]) / mask / fake values | plassholdere / maskering / fiktive verdier |
| knowledge base | kunnskapsbase |

## Interface

| English | Norwegian Bokmål |
|---|---|
| settings | innstillinger |
| dashboard | dashbord ("Overview" stays "Oversikt", Open WebUI's word) |
| save | lagre |
| cancel | avbryt |
| delete | slett |
| edit | rediger |
| search | søk |
| filter | filter (verb: filtrer) |
| export / import | eksporter / importer |
| upload / download | last opp / last ned |
| apply | bruk |
| confirm | bekreft |
| close / back | lukk / tilbake |
| next / previous | neste / forrige |
| create / add / remove | opprett / legg til / fjern |
| refresh | oppdater |
| retry | prøv igjen |
| reset | tilbakestill |
| undo | angre |
| sync / synced | synkroniser / synkronisert |
| key (encryption) | nøkkel |
| preview | forhåndsvisning |
| details | detaljer |
| loading… | laster inn… |
| error / warning | feil / advarsel |
| required / optional | påkrevd / valgfritt |
| user / group / permission / role | bruker / gruppe / tillatelse / rolle |
| admin / superadmin | administrator / superadministrator |
| sign in / sign out | logg inn / logg ut |
| language / theme | språk / tema |
| status | status |
