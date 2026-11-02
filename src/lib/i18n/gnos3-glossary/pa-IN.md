# Gnos3 — Punjabi (pa-IN, Gurmukhi) glossary

Translators of Gnos3, Finances, K4mi, Open WebUI and the expense app follow these terms so one word means one thing everywhere. UI words follow Gnos3's existing `pa-IN/translation.json` (Open WebUI) where it has them; K4mi's Punjabi catalog is empty, so document words are set here; accounting terms follow the words Punjab accountants use (Punjabi accountancy textbooks plus the English loanwords common in Indian practice — Tally, GST — written in Gurmukhi).

## Conventions

- **Register**: polite "ਤੁਸੀਂ / ਤੁਹਾਡਾ" form throughout (never "ਤੂੰ"). Instructions use the polite imperative in "-ੋ": "ਚੁਣੋ", "ਦਰਜ ਕਰੋ", "ਮੁੜ ਕੋਸ਼ਿਸ਼ ਕਰੋ". "ਕਿਰਪਾ ਕਰਕੇ" only where a request really needs it.
- **Buttons**: short imperative, verb last: "ਸੰਭਾਲੋ", "ਮਿਟਾਓ", "ਐਂਟਰੀ ਬਣਾਓ", "ਪੋਸਟ ਕਰੋ". Labels and column headings are nouns: "ਰਕਮ", "ਮਿਤੀ", "ਸਥਿਤੀ".
- **Product names and codes** stay as written: Gnos3, K4mi, SmartOffice, Ollama, Open WebUI, Excel, PDF, CSV, JSON, API, IBAN, currency codes (EUR, HKD), units, account codes, references (VAT-2026-09).
- **Punctuation**: a full sentence ends with the ਡੰਡੀ "।" (as in the Open WebUI Punjabi file); "?" and "!" as in English; ":" after a label with no space before it; double quotes "…" around quoted UI labels and names; "ਜਿਵੇਂ" for "e.g."; "ਆਦਿ" for "etc."; an ellipsis "…" stays (also at the end of "ਲੋਡ ਹੋ ਰਿਹਾ ਹੈ…").
- **Spelling**: write the pair-bindi forms Punjabi spells (ਫ਼ਾਈਲ, ਫ਼ਿਲਟਰ, ਦਸਤਾਵੇਜ਼, ਜ਼ਰੂਰੀ, ਮਨਜ਼ੂਰ); tippi/bindi as standard (ਮਿਆਦਾਂ, ਐਂਟਰੀਆਂ, ਕੰਪਨੀਆਂ).
- **Numbers and dates**: Western digits 0–9 (never Gurmukhi digits ੦–੯); amounts, dates and month names are formatted by the app — do not rewrite them. Keep `{{placeholder}}` / `{placeholder}` and `<0>…</0>` tags exactly; move them where Punjabi word order (SOV) needs them: "{{count}} ਐਂਟਰੀਆਂ ਪੋਸਟ ਕੀਤੀਆਂ ਗਈਆਂ".
- **Gender/agreement**: ਐਂਟਰੀ, ਇਨਵੌਇਸ, ਮਿਆਦ, ਕੰਪਨੀ, ਫ਼ਾਈਲ, ਲਾਈਨ, ਸ਼ੀਟ, ਦਰ are feminine (ਐਂਟਰੀ ਪੋਸਟ ਕੀਤੀ ਗਈ); ਖਾਤਾ, ਦਸਤਾਵੇਜ਼, ਭੁਗਤਾਨ, ਨਿਯਮ, ਟੈਗ, ਟੈਕਸ, ਕਾਰਡ are masculine (ਖਾਤਾ ਬਣਾਇਆ ਗਿਆ). A `{tax}` / `{{tax}}` slot is treated as masculine (ਟੈਕਸ, ਵੈਟ, ਜੀਐਸਟੀ): "{tax} ਦੇਣਯੋਗ ਹੈ".
- **DR / CR** in column headings: "ਡੈਬਿਟ" / "ਕ੍ਰੈਡਿਟ" (short: "ਡੈ." / "ਕ੍ਰੈ."). Do not use "ਨਾਮੇ / ਜਮ੍ਹਾਂ": ਨਾਮ = Name and ਜਮ੍ਹਾਂ ਕਰੋ = Submit on the same screens.
- **Void vs cancel vs reject**: Cancel (close a dialog) = "ਰੱਦ ਕਰੋ"; Void (an entry / a match) = "ਨਿਰਸਤ ਕਰੋ" / "ਨਿਰਸਤ"; Reject (an expense sheet) = "ਨਾਮਨਜ਼ੂਰ ਕਰੋ". The three never read alike.
- **Delete vs remove**: Delete (gone for good) = "ਮਿਟਾਓ"; Remove (take out of a list / unlink) = "ਹਟਾਓ" — as in the Open WebUI file.
- **ALL-CAPS** statement totals: Gurmukhi has no capitals; write them normally.

## Accounting and finance

| English | Punjabi |
|---|---|
| account (ledger account) | ਖਾਤਾ |
| account code / account name | ਖਾਤਾ ਕੋਡ / ਖਾਤੇ ਦਾ ਨਾਮ |
| chart of accounts | ਖਾਤਿਆਂ ਦਾ ਚਾਰਟ |
| chart template | ਚਾਰਟ ਟੈਮਪਲੇਟ |
| control account | ਕੰਟਰੋਲ ਖਾਤਾ |
| sub-account | ਉਪ-ਖਾਤਾ |
| detail / leaf account | ਵੇਰਵਾ ਖਾਤਾ (ਆਖਰੀ ਪੱਧਰ) |
| account type | ਖਾਤੇ ਦੀ ਕਿਸਮ |
| journal entry / entry / transaction (booked) | ਜਰਨਲ ਐਂਟਰੀ / ਐਂਟਰੀ |
| entry line / line | ਐਂਟਰੀ ਲਾਈਨ / ਲਾਈਨ |
| journal | ਜਰਨਲ |
| ledger | ਲੈਜਰ |
| general ledger | ਜਨਰਲ ਲੈਜਰ |
| sub-ledger | ਸਹਾਇਕ ਲੈਜਰ |
| trial balance | ਟਰਾਇਲ ਬੈਲੈਂਸ |
| balance sheet | ਬੈਲੈਂਸ ਸ਼ੀਟ |
| profit and loss / P&L / income statement | ਲਾਭ-ਹਾਨੀ / ਲਾਭ-ਹਾਨੀ ਬਿਆਨ |
| statement of financial position (HK) | ਵਿੱਤੀ ਸਥਿਤੀ ਦਾ ਬਿਆਨ |
| statement of profit or loss (HK) | ਲਾਭ ਜਾਂ ਹਾਨੀ ਦਾ ਬਿਆਨ |
| assets / current / non-current | ਸੰਪਤੀਆਂ / ਚਾਲੂ / ਗੈਰ-ਚਾਲੂ |
| liabilities | ਦੇਣਦਾਰੀਆਂ |
| equity | ਇਕੁਇਟੀ |
| retained earnings | ਬਰਕਰਾਰ ਕਮਾਈ |
| revenue / income | ਮਾਲੀਆ / ਆਮਦਨ |
| expense (account type, P&L, dashboards) | ਖਰਚਾ / ਖਰਚੇ |
| cost of sales | ਵਿਕਰੀ ਦੀ ਲਾਗਤ |
| gross profit / net profit | ਕੁੱਲ ਲਾਭ / ਸ਼ੁੱਧ ਲਾਭ |
| fiscal year / FY | ਵਿੱਤੀ ਸਾਲ / ਵਿ.ਸਾ. |
| year to date (YTD) | ਸਾਲ ਵਿੱਚ ਹੁਣ ਤੱਕ (YTD) |
| accounting period / period | ਲੇਖਾ ਮਿਆਦ / ਮਿਆਦ |
| close / reopen a period | ਮਿਆਦ ਬੰਦ ਕਰੋ / ਮੁੜ ਖੋਲ੍ਹੋ |
| year-end closing | ਸਾਲ-ਅੰਤ ਸਮਾਪਤੀ |
| closing checklist | ਸਮਾਪਤੀ ਜਾਂਚ-ਸੂਚੀ |
| opening balance | ਸ਼ੁਰੂਆਤੀ ਬਕਾਇਆ |
| closing balance | ਅੰਤਿਮ ਬਕਾਇਆ |
| balance (amount left) | ਬਕਾਇਆ |
| debit / credit | ਡੈਬਿਟ / ਕ੍ਰੈਡਿਟ |
| draft | ਡਰਾਫਟ |
| post / posted | ਪੋਸਟ ਕਰੋ / ਪੋਸਟ ਕੀਤੀ |
| void / voided | ਨਿਰਸਤ ਕਰੋ / ਨਿਰਸਤ |
| reversal (entry) | ਉਲਟ ਐਂਟਰੀ |
| book (an invoice) / booking | ਬੁੱਕ ਕਰੋ / ਬੁਕਿੰਗ |
| booking defaults | ਡਿਫਾਲਟ ਬੁਕਿੰਗ ਖਾਤੇ |
| gap (line awaiting an account) | ਅਧੂਰੀ ਲਾਈਨ (ਖਾਤਾ ਬਾਕੀ) |
| incomplete (entry with gaps) | ਅਧੂਰੀ |
| blocker | ਰੁਕਾਵਟ |
| invoice | ਇਨਵੌਇਸ |
| bill (supplier invoice) | ਸਪਲਾਇਰ ਇਨਵੌਇਸ |
| receipt | ਰਸੀਦ |
| payment | ਭੁਗਤਾਨ |
| inbound / outbound payment | ਪ੍ਰਾਪਤ ਭੁਗਤਾਨ / ਕੀਤਾ ਗਿਆ ਭੁਗਤਾਨ |
| payment method | ਭੁਗਤਾਨ ਦਾ ਤਰੀਕਾ |
| bank transfer / cheque / credit card / cash | ਬੈਂਕ ਟ੍ਰਾਂਸਫਰ / ਚੈੱਕ / ਕ੍ਰੈਡਿਟ ਕਾਰਡ / ਨਕਦ |
| payer / payee | ਭੁਗਤਾਨਕਰਤਾ / ਪ੍ਰਾਪਤਕਰਤਾ |
| supplier / vendor | ਸਪਲਾਇਰ |
| customer / client | ਗਾਹਕ |
| counterparty | ਦੂਜੀ ਧਿਰ |
| accounts payable / receivable (AP / AR) | ਦੇਣਯੋਗ ਖਾਤੇ / ਪ੍ਰਾਪਤੀਯੋਗ ਖਾਤੇ |
| AP / AR aging | ਦੇਣਯੋਗ / ਪ੍ਰਾਪਤੀਯੋਗ ਉਮਰ-ਵਿਸ਼ਲੇਸ਼ਣ |
| bank account | ਬੈਂਕ ਖਾਤਾ |
| bank statement | ਬੈਂਕ ਸਟੇਟਮੈਂਟ |
| bank line / statement line | ਬੈਂਕ ਲਾਈਨ |
| bank reconciliation | ਬੈਂਕ ਮਿਲਾਨ |
| match / unmatch / matched | ਮਿਲਾਨ ਕਰੋ / ਮਿਲਾਨ ਹਟਾਓ / ਮਿਲਾਨ ਹੋਇਆ |
| match group | ਮਿਲਾਨ ਸਮੂਹ |
| auto-match | ਆਟੋ-ਮਿਲਾਨ |
| exchange rate | ਵਟਾਂਦਰਾ ਦਰ |
| exchange difference / gain / loss | ਵਟਾਂਦਰਾ ਅੰਤਰ / ਵਟਾਂਦਰਾ ਲਾਭ / ਵਟਾਂਦਰਾ ਹਾਨੀ |
| exchange clearing account | ਵਟਾਂਦਰਾ ਕਲੀਅਰਿੰਗ ਖਾਤਾ |
| base currency | ਆਧਾਰ ਮੁਦਰਾ |
| currency | ਮੁਦਰਾ |
| rate override | ਵਿਸ਼ੇਸ਼ ਦਰ |
| categorization rule | ਸ਼੍ਰੇਣੀਕਰਨ ਨਿਯਮ |
| bank-line rule | ਬੈਂਕ ਲਾਈਨ ਨਿਯਮ |
| pattern | ਪੈਟਰਨ |
| split (across accounts) | ਵੰਡ / ਵੰਡੋ |
| fixed asset | ਸਥਿਰ ਸੰਪਤੀ |
| depreciation / accumulated depreciation | ਘਸਾਈ / ਸੰਚਿਤ ਘਸਾਈ |
| useful life / salvage value / book value | ਉਪਯੋਗੀ ਜੀਵਨ / ਬਚਤ ਮੁੱਲ / ਬੁੱਕ ਮੁੱਲ |
| straight-line / declining balance | ਸਿੱਧੀ ਰੇਖਾ / ਘਟਦਾ ਬਕਾਇਆ |
| expense sheet | ਖਰਚਾ ਸ਼ੀਟ |
| expenses (the expense-claims tab, `Expenses_tab`) | ਖਰਚਾ ਸ਼ੀਟਾਂ |
| reimbursement | ਭਰਪਾਈ |
| employee | ਕਰਮਚਾਰੀ |
| approve / reject / submit | ਮਨਜ਼ੂਰ ਕਰੋ / ਨਾਮਨਜ਼ੂਰ ਕਰੋ / ਜਮ੍ਹਾਂ ਕਰੋ |
| company | ਕੰਪਨੀ |
| legal entity name | ਕਾਨੂੰਨੀ ਨਾਮ |
| template | ਟੈਮਪਲੇਟ |

## Tax

| English | Punjabi |
|---|---|
| tax | ਟੈਕਸ |
| VAT / GST / sales tax / consumption tax | ਵੈਟ / ਜੀਐਸਟੀ / ਵਿਕਰੀ ਟੈਕਸ / ਖਪਤ ਟੈਕਸ |
| output / input VAT | ਆਉਟਪੁੱਟ ਵੈਟ / ਇਨਪੁੱਟ ਵੈਟ |
| VAT payable / VAT credit | ਦੇਣਯੋਗ ਵੈਟ / ਵੈਟ ਕ੍ਰੈਡਿਟ |
| credit brought / carried forward | ਪਿਛਲਾ ਲਿਆਂਦਾ ਕ੍ਰੈਡਿਟ / ਅੱਗੇ ਲਿਜਾਇਆ ਕ੍ਰੈਡਿਟ |
| surcharge (China) | ਸਰਚਾਰਜ |
| corporate income tax (CIT) | ਕਾਰਪੋਰੇਟ ਆਮਦਨ ਟੈਕਸ |
| individual income tax (IIT) | ਨਿੱਜੀ ਆਮਦਨ ਟੈਕਸ |
| profits tax (Hong Kong) | ਲਾਭ ਟੈਕਸ |
| provisional tax | ਆਰਜ਼ੀ ਟੈਕਸ |
| prepaid tax | ਅਗਾਊਂ ਅਦਾ ਟੈਕਸ |
| assessment notice / demand note | ਟੈਕਸ ਨਿਰਧਾਰਨ ਨੋਟਿਸ / ਮੰਗ ਨੋਟਿਸ |
| tax return / filing | ਟੈਕਸ ਰਿਟਰਨ / ਫ਼ਾਈਲਿੰਗ |
| accrual entry | ਐਕਰੂਅਲ ਐਂਟਰੀ |
| settlement entry / settle | ਨਿਪਟਾਰਾ ਐਂਟਰੀ / ਨਿਪਟਾਰਾ ਕਰੋ |
| add-back / deduction | ਵਾਪਸ ਜੋੜ / ਕਟੌਤੀ |
| tax adjustments | ਟੈਕਸ ਸਮਾਯੋਜਨ |
| assessable profit | ਟੈਕਸਯੋਗ ਲਾਭ |
| losses brought forward | ਪਿਛਲੇ ਲਿਆਂਦੇ ਘਾਟੇ |
| two-tier / tiered rates | ਦੋ-ਪੱਧਰੀ ਦਰਾਂ / ਪੱਧਰੀ ਦਰਾਂ |
| tax role mapping / mapped | ਮੈਪਿੰਗ / ਮੈਪ ਕੀਤਾ |
| due date | ਨਿਯਤ ਮਿਤੀ |

## Documents (K4mi)

| English | Punjabi |
|---|---|
| document | ਦਸਤਾਵੇਜ਼ |
| tag | ਟੈਗ |
| custom field | ਕਸਟਮ ਫ਼ੀਲਡ |
| correspondent | ਪੱਤਰ-ਵਿਹਾਰੀ |
| document type | ਦਸਤਾਵੇਜ਼ ਦੀ ਕਿਸਮ |
| storage path | ਸਟੋਰੇਜ ਪਾਥ |
| workflow | ਵਰਕਫ਼ਲੋ |
| owner | ਮਾਲਕ |
| note / notes | ਨੋਟ / ਨੋਟਸ |
| saved view | ਸੰਭਾਲਿਆ ਦ੍ਰਿਸ਼ |
| file | ਫ਼ਾਈਲ |
| business card | ਵਿਜ਼ਿਟਿੰਗ ਕਾਰਡ |
| needs review / mark reviewed | ਸਮੀਖਿਆ ਲੋੜੀਂਦੀ / ਸਮੀਖਿਆ ਹੋਈ ਵਜੋਂ ਚਿੰਨ੍ਹਿਤ ਕਰੋ |
| extraction / extract | ਡਾਟਾ ਕੱਢਣਾ / ਕੱਢੋ |
| confidence | ਭਰੋਸਾ ਪੱਧਰ |
| reprocess | ਮੁੜ ਪ੍ਰੋਸੈਸ ਕਰੋ |

## Interface

| English | Punjabi |
|---|---|
| settings | ਸੈਟਿੰਗਾਂ |
| dashboard | ਡੈਸ਼ਬੋਰਡ |
| save | ਸੰਭਾਲੋ |
| cancel | ਰੱਦ ਕਰੋ |
| delete / remove | ਮਿਟਾਓ / ਹਟਾਓ |
| edit | ਸੰਪਾਦਨ ਕਰੋ |
| create / add | ਬਣਾਓ / ਸ਼ਾਮਲ ਕਰੋ |
| search | ਖੋਜੋ (noun: ਖੋਜ) |
| filter | ਫ਼ਿਲਟਰ |
| export / import | ਨਿਰਯਾਤ ਕਰੋ / ਆਯਾਤ ਕਰੋ |
| upload / download | ਅਪਲੋਡ ਕਰੋ / ਡਾਊਨਲੋਡ ਕਰੋ |
| apply | ਲਾਗੂ ਕਰੋ |
| confirm | ਪੁਸ਼ਟੀ ਕਰੋ |
| close | ਬੰਦ ਕਰੋ |
| refresh | ਤਾਜ਼ਾ ਕਰੋ |
| retry | ਮੁੜ ਕੋਸ਼ਿਸ਼ ਕਰੋ |
| loading… | ਲੋਡ ਹੋ ਰਿਹਾ ਹੈ… |
| error / warning | ਗਲਤੀ / ਚੇਤਾਵਨੀ |
| status | ਸਥਿਤੀ |
| date / amount / total | ਮਿਤੀ / ਰਕਮ / ਕੁੱਲ |
| description | ਵੇਰਵਾ |
| reference | ਹਵਾਲਾ |
| user / group / role / permissions | ਉਪਭੋਗਤਾ / ਸਮੂਹ / ਭੂਮਿਕਾ / ਅਨੁਮਤੀਆਂ |
| admin | ਪ੍ਰਬੰਧਕ |
| preview | ਝਲਕ |
| optional / required | ਵਿਕਲਪਿਕ / ਲਾਜ਼ਮੀ |
| enabled / disabled | ਚਾਲੂ / ਬੰਦ |
| pending | ਲੰਬਿਤ |
| failed | ਅਸਫਲ |
| anonymise / Anonymiser (the module) | ਗੁਮਨਾਮ ਕਰੋ / ਗੁਮਨਾਮੀਕਰਨ |
| decrypt | ਡੀਕ੍ਰਿਪਟ ਕਰੋ |
