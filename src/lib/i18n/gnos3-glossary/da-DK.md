# Gnos3 — Danish (da-DK) glossary

## Conventions

- **Form of address**: "du" (the normal register of Danish business software: e-conomic, Dinero, Microsoft). Never "De". Polite but direct: "Vælg en konto", "Du kan ikke fortryde dette."
- **Buttons**: imperative, short, sentence case: "Gem", "Opret postering", "Bogfør", "Eksporter til Excel". Imperatives without accent (Rediger, Eksporter, Importer, Annuller, Marker); "Eksportér" in the Open WebUI file is tolerated, but new strings drop the accent.
- **Sentence case**; Danish lower-cases month and weekday names, languages and nationality adjectives (januar, mandag, dansk). Only the first word and proper names take a capital.
- **Compounds are written as one word** (momsangivelse, bankafstemning, kontoplan). After an abbreviation, a product name, a number or a placeholder use a hyphen: K4mi-etiket, PDF-fil, CSV-fil, Excel-fil, AI-forslag, MPF-bidrag, {{name}}-skabelon.
- **Punctuation**: no space before ":" "?" "!". Quoted UI labels and names in »…« (»{{name}}« slettes). Ellipsis as "…". "e.g." = "f.eks.", "i.e." = "dvs.", "etc." = "osv.", "approx." = "ca.". Comma before subordinate clauses (grammatical comma, no start comma): "Vælg den konto, som beløbet skal bogføres på."
- **Numbers and dates** (when written in text, e.g. placeholders in examples): decimal comma and thousands point (1.234,56); amounts with the currency code after or before as the screen shows it (DKK 1.234,56 / 1.234,56 kr.); dates dd.mm.åååå or "31. marts 2026"; percent with a space: "25 %".
- **Debit / credit** columns: "Debet" / "Kredit"; abbreviations DR / CR → D / K.
- **Statement totals** written in ALL CAPS in the source stay in capitals.
- **Tax placeholders**: UI `{{tax}}` / books `{tax}` is filled with a capitalised term ("Moms", "GST", "Forbrugsafgift"); put it first or after a colon / parenthesis when natural ("{{tax}} til betaling", "Angivelse: {{tax}}"); otherwise accept it mid-sentence ("Udgående {{tax}}"). `{{cit}}` is "Selskabsskat" / "Overskudsskat".
- **Account (Open WebUI)** = the user's profile ("Profil", existing file); **Account_gnos3** = a ledger account ("Konto").
- Plural of konto: "konti", definite "kontiene" ("alle konti", "de valgte konti", "kontiene i kontoplanen").

## Accounting and finance

| English | Danish |
|---|---|
| account (ledger) | konto (pl. konti) |
| account name / account code | kontonavn / kontonummer |
| account type | kontotype |
| chart of accounts | kontoplan |
| control account (with sub-accounts) | samlekonto |
| sub-account | underkonto |
| detail / leaf account | posteringskonto |
| journal entry / entry / transaction | postering |
| entry line | posteringslinje |
| manual voucher / voucher | bilag / manuelt bilag |
| journal | journal |
| general ledger | hovedbog |
| sub-ledger | reskontro |
| trial balance | saldobalance |
| balance sheet | balance |
| income statement / P&L / profit and loss | resultatopgørelse |
| statement of financial position (HK) | opgørelse over finansiel stilling |
| statement of profit or loss (HK) | resultatopgørelse |
| assets / liabilities | aktiver / forpligtelser (gæld) |
| current / non-current assets | omsætningsaktiver / anlægsaktiver |
| current / non-current liabilities | kortfristede / langfristede gældsforpligtelser |
| equity | egenkapital |
| retained earnings | overført resultat |
| revenue / income | omsætning / indtægter |
| cost of sales / COGS | vareforbrug |
| gross profit | bruttoresultat |
| operating profit | driftsresultat |
| net income / profit for the year | årets resultat |
| administrative expenses | administrationsomkostninger |
| financial expenses / finance costs | finansielle omkostninger |
| expenses (account type, P&L, dashboards) | omkostninger |
| opening balance | primosaldo (opening balance sheet: åbningsbalance) |
| closing balance | ultimosaldo |
| balance (of an account) | saldo |
| debit / credit | debet / kredit |
| draft | kladde |
| post / posted | bogføre / bogført |
| book (an invoice), booking | kontere, kontering |
| booking defaults | standardkonteringer |
| booking engine | konteringsmotor |
| gap (line awaiting an account) | manglende kontering |
| void / voided | annullere / annulleret ("Void" button = "Annuller postering", never bare "Annuller" = Cancel) |
| reversal / reverse | tilbageførsel / tilbageføre |
| accounting period | regnskabsperiode |
| fiscal year / FY | regnskabsår |
| year to date (YTD) | år til dato (ÅTD) |
| year-end closing | årsafslutning |
| close / reopen (a period) | lukke / genåbne |
| closing checklist | afslutningstjekliste |
| blocker | blokerende punkt |
| bank reconciliation | bankafstemning |
| match / unmatch / matched | afstemme / ophæve afstemning / afstemt |
| match group | afstemningsgruppe |
| auto-match | automatisk afstemning |
| bank statement / bank line | kontoudtog / banklinje |
| bank account | bankkonto |
| counterparty | modpart |
| accounts payable (AP) | leverandørgæld (kreditorer) |
| accounts receivable (AR) | tilgodehavender fra salg (debitorer) |
| AP / AR aging | aldersfordelt kreditor- / debitorliste |
| aging bucket / "Current" bucket | aldersinterval / ikke forfalden |
| supplier / vendor | leverandør |
| customer / client | kunde |
| bill (supplier invoice) | leverandørfaktura |
| sales invoice | salgsfaktura |
| invoice | faktura (pl. fakturaer) |
| receipt | kvittering |
| payment | betaling |
| payment in / out | indbetaling / udbetaling |
| payer / payee | betaler / betalingsmodtager |
| payment method | betalingsmetode |
| bank transfer / check / credit card / cash | bankoverførsel / check / kreditkort / kontant |
| due date | forfaldsdato |
| amount | beløb |
| company | virksomhed |
| legal entity name | juridisk navn |
| currency / base currency | valuta / basisvaluta |
| exchange rate | valutakurs |
| exchange difference / gain / loss | kursdifference / kursgevinst / kurstab |
| exchange clearing account | mellemregningskonto for valuta |
| rate override (company rate) | virksomhedsspecifik kurs |
| categorization rule | kategoriseringsregel |
| bank-line rule | banklinjeregel |
| pattern | mønster |
| split (across accounts) | fordele, fordeling |
| template | skabelon |
| fixed asset | anlægsaktiv |
| depreciation / accumulated depreciation | afskrivning / akkumulerede afskrivninger |
| useful life / salvage value / book value | brugstid / restværdi / regnskabsmæssig værdi |
| straight-line / declining balance | lineær / saldometode |
| asset register | anlægskartotek |
| expense sheet | udlægsrapport |
| expenses (the expense-claims tab, `Expenses_tab`) | udlæg |
| expense receipt | kvittering |
| reimbursement | refusion |
| employee | medarbejder |
| approve / reject / submit | godkende / afvise / indsende |
| VAT | moms |
| tax (amount / rate on an invoice, generic) | afgift (afgiftsbeløb, afgiftssats, inkl. afgift) |
| Tax tab (`Tax_tab`) | Skat |
| GST / GST/HST / consumption tax / sales tax / ICMS | GST / GST/HST / forbrugsafgift / salgsafgift / ICMS |
| output / input VAT | udgående moms (salgsmoms) / indgående moms (købsmoms) |
| VAT payable / VAT credit | skyldig moms / momstilgodehavende |
| credit brought forward / carried forward | overført tilgodehavende / tilgodehavende til fremførsel |
| VAT surcharge (China) | tillægsafgift |
| corporate income tax (CIT) | selskabsskat |
| individual income tax (IIT) | personlig indkomstskat |
| profits tax (Hong Kong) | overskudsskat (Profits Tax) |
| provisional tax | acontoskat |
| prepaid tax (asset) | forudbetalt skat |
| assessment notice / demand note | skatteansættelse / opkrævning |
| tax return / filing | angivelse |
| accrual entry (tax) | hensættelsespostering |
| settlement entry (VAT) | afregningspostering |
| settle | afregne |
| add-back / deduction | tillæg / fradrag |
| tax computation adjustments | skattemæssige reguleringer |
| assessable profit | skattepligtig indkomst |
| losses brought forward | fremførte underskud |
| two-tier / tiered rates | totrinssats / trinvise satser |
| tax role mapping / mapped | tilknytning / tilknyttet |
| MPF (HK pension) | MPF (pensionsbidrag) |

## Documents (K4mi) and modules

| English | Danish |
|---|---|
| document | dokument |
| tag (K4mi) | etiket (K4mi-etiket), as in K4mi's catalog |
| custom field | brugerdefineret felt |
| correspondent | korrespondent |
| document type | dokumenttype |
| storage path | lagringssti |
| archive serial number | arkivserienummer |
| inbox | indbakke |
| owner | ejer |
| workflow | arbejdsgang |
| webhook | webhook |
| OCR | OCR |
| extraction / extract | udtrækning / udtrække |
| reprocess | behandl igen |
| business card | visitkort |
| needs review / mark reviewed | kræver gennemgang / marker som gennemgået |
| confidence | sikkerhed |
| anonymise (button) / the Anonymiser module | Anonymiser / Anonymisering (module and page name) |
| labels mode ([PERSON_1]) / mask / fake values | pladsholdere / maskering / fiktive værdier |
| knowledge base | vidensbase |

## Interface

| English | Danish |
|---|---|
| settings | indstillinger |
| dashboard | oversigt (K4mi's older catalog says "Betjeningspanel"; new strings use "Oversigt") |
| save | gem |
| cancel | annuller (Open WebUI's file has "Afbryd" for the bare button; new strings use "Annuller", as K4mi does) |
| delete | slet |
| edit | rediger |
| search | søg |
| filter | filter (verb: filtrer) |
| export / import | eksporter / importer |
| upload / download | upload / download (verb: uploade / downloade) |
| apply | anvend |
| confirm | bekræft |
| close / back | luk / tilbage |
| next / previous | næste / forrige |
| create / add / remove | opret / tilføj / fjern |
| refresh | opdater |
| retry | prøv igen |
| reset | nulstil |
| undo | fortryd |
| sync / synced | synkroniser / synkroniseret |
| key (encryption) | nøgle |
| preview | forhåndsvisning |
| details | detaljer |
| loading… | indlæser… |
| error / warning | fejl / advarsel |
| required / optional | påkrævet / valgfri |
| user / group / permission / role | bruger / gruppe / tilladelse / rolle |
| admin / superadmin | administrator / superadministrator |
| sign in / sign out | log ind / log ud |
| language / theme | sprog / tema |
| status | status |
