# Gnos3 — Swedish (sv-SE) glossary

## Conventions

- **Form of address**: "du" (the normal register of Swedish business software: Fortnox, Visma, Microsoft). Never "ni". Polite but direct: "Välj ett konto", "Det går inte att ångra."
- **Buttons**: imperative, short, sentence case: "Spara", "Skapa verifikation", "Bokför", "Exportera till Excel". Menu and tab names are nouns ("Inställningar", "Översikt", "Verifikationer").
- **Sentence case**. Swedish lower-cases month and weekday names, languages and nationality adjectives (januari, måndag, svenska). Only the first word and proper names take a capital.
- **Compounds are written as one word** (momsdeklaration, bankavstämning, kontoplan, leverantörsfaktura). After an abbreviation, a product name, a number or a code use a hyphen: K4mi-tagg, PDF-fil, CSV-fil, Excel-fil, AI-förslag, MPF-avgift. Do not glue a word to a `{{placeholder}}`: write "mallen {{name}}", "deklaration ({{tax}})", not "{{name}}-mallen".
- **Punctuation**: no space before ":" "?" "!". Quoted UI labels and names in Swedish quotation marks ”…” (the same mark on both sides): ”{{name}}” tas bort. Ellipsis as "…". "e.g." = "t.ex.", "i.e." = "dvs.", "etc." = "osv.", "approx." = "ca", "incl." = "inkl.", "excl." = "exkl.". Em dash "—" may stay as in the source; Swedish prefers a spaced en dash " – " in running text, either is fine.
- **Numbers and dates** (when written in text, e.g. examples): decimal comma, space as thousands separator (1 234,56); currency code after the amount (1 234,56 SEK) or as the screen shows it; percent with a space: "25 %". Dates in ISO form 2026-03-31 (Swedish standard) or "31 mars 2026"; times 14:30.
- **Debit / credit** columns: "Debet" / "Kredit"; abbreviations DR / CR → D / K.
- **Statement totals** written in ALL CAPS in the source stay in capitals (SUMMA TILLGÅNGAR).
- **Tax placeholders**: UI `{{tax}}` / books `{tax}` is filled with a capitalised term ("Moms", "GST", "Konsumtionsskatt", "Försäljningsskatt"); put it first or after a colon / in parentheses when natural ("{{tax}} att betala", "Deklaration: {{tax}}", "Utgående skatt ({{tax}})"); otherwise accept it mid-sentence. `{{cit}}` is "Bolagsskatt" / "Vinstskatt (Hongkong)". "VAT" alone = "Moms".
- **Account (Open WebUI)** = the user's sign-in account ("Konto", existing file); **Account_gnos3** = a ledger account ("Konto"). Plural "konton", definite "kontot" / "kontona".
- **Entry**: a journal entry is a "verifikation" (pl. verifikationer); its lines are "rader" / "konteringsrader". "Transaction" in the accounting sense is also "verifikation"; a bank transaction is a "banktransaktion" / "bankrad".
- **Remove vs delete**: "Delete" (destroys data) = "Radera" (existing Open WebUI / K4mi word); "Remove" (takes out of a list / unlinks) = "Ta bort".

## Accounting and finance

| English | Swedish |
|---|---|
| account (ledger) | konto (pl. konton) |
| account name / account code | kontonamn / kontonummer |
| account type | kontotyp |
| chart of accounts | kontoplan |
| control account (with sub-accounts) | samlingskonto |
| sub-account | underkonto |
| detail / leaf account | detaljkonto |
| journal entry / entry / transaction | verifikation |
| entry line | verifikationsrad / konteringsrad |
| manual voucher / voucher | manuell verifikation / verifikation |
| journal (chronological view) | grundbok |
| general ledger | huvudbok |
| sub-ledger | reskontra |
| trial balance | saldobalans |
| balance sheet | balansräkning |
| income statement / P&L / profit and loss | resultaträkning |
| statement of financial position (HK) | rapport över finansiell ställning |
| statement of profit or loss (HK) | rapport över resultat |
| assets / liabilities | tillgångar / skulder |
| current / non-current assets | omsättningstillgångar / anläggningstillgångar |
| current / non-current liabilities | kortfristiga / långfristiga skulder |
| equity | eget kapital |
| retained earnings | balanserat resultat |
| revenue / income | intäkter |
| expenses (account type, P&L) | kostnader |
| cost of sales | kostnad sålda varor |
| gross profit / net income | bruttoresultat / årets resultat (nettoresultat) |
| opening balance | ingående balans (IB) |
| closing balance | utgående balans (UB) |
| carry-forward entry | ingående balansverifikation |
| draft | utkast |
| post / posted | bokföra / bokförd |
| book (an invoice) / booking | kontera / kontering |
| booking defaults | standardkonteringar |
| booking engine | konteringsmotor |
| gap (line awaiting an account) | saknad kontering (rad utan konto) |
| void / voided | makulera / makulerad |
| reversal (entry) | återföring |
| accounting period | redovisningsperiod (period) |
| fiscal year / FY | räkenskapsår / RÅ |
| year-end closing | bokslut (årsbokslut) |
| year to date (YTD) | ackumulerat (hittills i år) |
| close / reopen a period | stäng / öppna igen |
| closing checklist | bokslutskontroller |
| blocker | hinder |
| bank reconciliation | bankavstämning |
| match / unmatch / matched | matcha / ta bort matchning / matchad |
| match group | matchningsgrupp |
| bank statement | kontoutdrag |
| bank line | bankrad |
| counterparty | motpart |
| accounts payable / receivable | leverantörsskulder / kundfordringar |
| AP / AR aging | åldersanalys leverantörsskulder / kundfordringar |
| aging bucket / "Current" bucket | intervall / ej förfallet |
| vendor / supplier | leverantör |
| customer / client | kund |
| invoice | faktura |
| bill (supplier invoice) | leverantörsfaktura |
| sales invoice | kundfaktura |
| credit note | kreditfaktura |
| receipt | kvitto |
| payment | betalning |
| payment in / out | inbetalning / utbetalning |
| payer / payee | betalare / betalningsmottagare |
| payment method | betalningssätt |
| bank transfer / check / credit card / cash | banköverföring / check / kreditkort / kontanter |
| currency | valuta |
| base currency | basvaluta |
| exchange rate | växelkurs |
| exchange difference / gain / loss | kursdifferens / kursvinst / kursförlust |
| exchange clearing account | valutaavräkningskonto |
| company rate override | företagsspecifik kurs |
| categorization rule | kategoriseringsregel |
| bank-line rule | bankradsregel |
| pattern | mönster |
| split (across accounts) | fördela, fördelning |
| fixed asset | anläggningstillgång (inventarie) |
| depreciation / accumulated depreciation | avskrivning / ackumulerade avskrivningar |
| useful life / salvage value / book value | nyttjandeperiod / restvärde / bokfört värde |
| linear / declining | linjär / degressiv |
| asset register | anläggningsregister |
| expense (one claim item) | utlägg |
| expense sheet / reimbursement sheet | utläggsredovisning |
| expenses (the expense-claims tab, key `Expenses_tab`) | utlägg |
| reimbursement | ersättning |
| employee | anställd |
| approve / reject / submit | godkänn / avvisa / skicka in |
| VAT | moms |
| GST / GST-HST / sales tax / consumption tax | GST / GST/HST / försäljningsskatt / konsumtionsskatt |
| output / input VAT | utgående moms / ingående moms |
| VAT payable / VAT credit | moms att betala / moms att återfå |
| credit brought forward / carried forward | överskott från föregående period / överskott att föra vidare |
| surcharge (China, on VAT) | tilläggsavgift |
| corporate income tax (CIT) | bolagsskatt |
| individual income tax (IIT) | inkomstskatt för fysiska personer |
| profits tax (Hong Kong) | vinstskatt |
| provisional tax | preliminärskatt |
| prepaid tax (asset) | förutbetald skatt |
| assessment notice / demand note | slutskattebesked / debiteringsbesked |
| tax return / filing | deklaration |
| accrual entry (tax) | periodiseringsverifikation |
| settlement entry (VAT) | avräkningsverifikation (momsavräkning) |
| settle (a filing) | reglera |
| add-back / deduction | tillägg / avdrag |
| tax computation adjustments | skattemässiga justeringar |
| assessable profit | skattepliktigt resultat |
| losses brought forward | underskott från tidigare år |
| two-tier / tiered rates | tvåstegssatser / skattesatser i steg |
| tax role mapping / mapped | koppling / kopplad |
| template | mall |
| company | företag |
| legal entity name | juridiskt namn |
| business card | visitkort |
| needs review / mark reviewed | behöver granskas / markera som granskad |
| amount / total / subtotal | belopp / summa / delsumma |
| net / gross | netto / brutto |
| due date | förfallodatum |

## Documents (K4mi)

| English | Swedish |
|---|---|
| document | dokument |
| tag / K4mi tag | tagg / K4mi-tagg |
| custom field | anpassat fält |
| correspondent | korrespondent |
| document type | dokumenttyp |
| storage path | lagringsplats |
| archive serial number (ASN) | arkivserienummer (ASN) |
| saved view | sparad vy |
| workflow | arbetsflöde |
| owner | ägare |
| inbox | inkorg |
| upload | ladda upp |
| original file / archived version | originalfil / arkiverad version |

## Interface

| English | Swedish |
|---|---|
| settings | inställningar |
| dashboard | översikt |
| save | spara |
| cancel | avbryt |
| delete | radera |
| remove | ta bort |
| edit | redigera |
| create / add | skapa / lägg till |
| search | sök |
| filter (noun / verb) | filter / filtrera |
| export / import | exportera / importera |
| upload / download | ladda upp / ladda ner |
| apply | tillämpa |
| confirm | bekräfta |
| close | stäng |
| refresh | uppdatera |
| reset / clear | återställ / rensa |
| loading… | läser in… |
| error / warning | fel / varning |
| permissions | behörigheter |
| group | grupp |
| status | status |
| details | detaljer |
| preview | förhandsgranska / förhandsvisning |
| review (verb) | granska |
| previous / next | föregående / nästa |
| optional / required | valfritt / obligatoriskt |
