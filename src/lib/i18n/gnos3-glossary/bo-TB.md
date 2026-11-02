# Gnos3 — Tibetan (བོད, bo-TB) glossary

Shared by every translator of this language (Gnos3 screens, server messages, Finances, K4mi, Open WebUI, the expense app). UI words follow Gnos3's existing `bo-TB/translation.json` (Open WebUI); K4mi's `bo_CN` catalog has no translations yet, so document words are set here. Accounting words follow the modern Tibetan financial vocabulary used in the PRC Tibetan areas (calques of 会计 terms: 借方 / 贷方 → གཡར་ཕྱོགས། / སྐྱིན་ཕྱོགས།).

## Conventions

- **Register**: polite, impersonal business Tibetan. Address the reader as ཁྱེད། / ཁྱེད་རང་། only when needed; requests end with …རོགས། ("please …"): ཡང་བསྐྱར་ཚོད་ལྟ་བྱེད་རོགས།
- **Buttons and labels**: short verb or noun phrase, verb last (ཉར་ཚགས།, རྩིས་འགོད་གསར་བཟོ།, ཁ་རྒྱག). No "please" on buttons.
- **Punctuation**: tsheg ་ between syllables; shad ། ends a label or sentence. No shad after a final ག (ཞུ་དག, ལག་བསྟར་བྱེད་ཆོག); after a final ང write ང་། (ཕྱིར་གཏོང་།, མིང་།). No Western full stop. Questions use a question particle (…ཡིན་ནམ། …བྱེད་དམ། …ཨེ་ཡིན།) and end with ། — no "?". Keep ":" after a field label and "…" for an action in progress. Quoted UI labels and names go in “ ”.
- **Placeholders** `{{x}}` / `{x}`: kept exactly, with a space on each side when they touch Tibetan text (ཚོང་འཛིན་ {{count}}). Tibetan verbs come last, so a placeholder often moves to the front of the sentence.
- **Numbers, amounts, dates**: Western digits 0–9 (the app formats amounts and dates); no Tibetan digits. Counts: noun then number (ཕྲེང་ {{count}}, ཉིན་ {{count}}). Plural forms are the same as the singular (Tibetan has no grammatical plural; ཚོ / དག only for people or emphasis).
- **Abbreviations**: DR → གཡར།  CR → སྐྱིན།  YTD → ལོ་འགོ་ནས་ད་བར།  FY → རྩིས་ལོ།  VAT → རིན་འཕར་ཁྲལ།  P&L → ཁེ་གྱོང་།  Product names (Gnos3, K4mi, SmartOffice, Ollama, Excel, PDF, CSV), currency codes (EUR, HKD), country codes and units stay in Latin script.
- **Two senses of "account"**: a sign-in / user account = རྩིས་ཁྲ། (Open WebUI's word); a ledger account (key `Account_gnos3`) = རྩིས་ཁོངས།; a bank account = དངུལ་ཁང་རྩིས་ཁྲ།
- **"Entry" / "transaction"** in accounting = རྩིས་འགོད། (one word for journal entry, entry, voucher-style transaction); a bank transaction / bank line = དངུལ་ཁང་ཐོ་ཕྲེང་།
- **Statuses** are past participles with ཟིན། / བྱས་ཟིན། (དེབ་འགོད་བྱས་ཟིན། posted, ནུས་མེད་བཏང་ཟིན། voided, ཆོག་མཆན་ཐོབ་ཟིན། approved).

## Accounting and finance

| English | བོད་ཡིག |
|---|---|
| accounting (module) | དངུལ་རྩིས། |
| accountant | དངུལ་རྩིས་པ། |
| account (ledger, `Account_gnos3`) | རྩིས་ཁོངས། |
| account code / account name | རྩིས་ཁོངས་ཨང་རྟགས། / རྩིས་ཁོངས་ཀྱི་མིང་། |
| chart of accounts | རྩིས་ཁོངས་རེའུ་མིག |
| sub-account | ཡན་ལག་རྩིས་ཁོངས། |
| control account (with sub-accounts) | ཚོད་འཛིན་རྩིས་ཁོངས། |
| detail / leaf account | མཐའ་མའི་རྩིས་ཁོངས། |
| journal entry / entry / transaction | རྩིས་འགོད། |
| voucher | རྩིས་འཛིན། |
| journal | ཉིན་ཐོ། |
| ledger | རྩིས་དེབ། |
| general ledger | སྤྱི་རྩིས་དེབ། |
| trial balance | ཚོད་རྩིས་སྙོམས་ཐོ། |
| balance sheet | རྒྱུ་ནོར་བུ་ལོན་རེའུ་མིག |
| profit and loss / income statement | ཁེ་གྱོང་རེའུ་མིག |
| financial statements | དཔལ་རྩིས་རེའུ་མིག |
| profit / loss / net income | ཁེ་བཟང་། / གྱོང་ཁ། / ཁེ་བཟང་གཙང་མ། |
| revenue / income | ཡོང་འབབ། |
| expenses (account type, P&L) | འགྲོ་སོང་། |
| cost of sales | བཙོང་ཟོང་མ་གནས། |
| asset / liability / equity | རྒྱུ་ནོར། / བུ་ལོན། / མ་རྩའི་དབང་ཆ། |
| current / non-current assets | འཁོར་སྐྱོད་རྒྱུ་ནོར། / འཁོར་སྐྱོད་མིན་པའི་རྒྱུ་ནོར། |
| retained earnings | ཉར་འཇོག་ཁེ་བཟང་། |
| fiscal year | རྩིས་ལོ། |
| accounting period / period | རྩིས་དུས། |
| year to date (YTD) | ལོ་འགོ་ནས་ད་བར། |
| balance | ལྷག་འབབ། |
| opening balance / closing balance | ཐོག་མའི་ལྷག་འབབ། / མཇུག་གི་ལྷག་འབབ། |
| debit (DR) / debit side | གཡར། / གཡར་ཕྱོགས། |
| credit (CR) / credit side | སྐྱིན། / སྐྱིན་ཕྱོགས། |
| draft | ཟིན་བྲིས། |
| post / posted | དེབ་འགོད། / དེབ་འགོད་བྱས་ཟིན། |
| void / voided | ནུས་མེད་གཏོང་། / ནུས་མེད་བཏང་ཟིན། |
| reversal (entry) | ལྡོག་འགོད། |
| book (an invoice) / booking | རྩིས་ཁོངས་སུ་འགོད། / རྩིས་ཁོངས་འགོད་པ། |
| booking defaults | རྩིས་ཁོངས་འགོད་པའི་སྔོན་སྒྲིག |
| gap (line awaiting an account) | སྟོང་ཆ། |
| blocker | བཀག་རྐྱེན། |
| close / reopen a period | རྩིས་དུས་སྒོ་རྒྱག / སླར་ཁ་ཕྱེ། |
| year-end close | ལོ་མཇུག་རྩིས་སྒྲིལ། |
| closing checklist | རྩིས་སྒྲིལ་ཞིབ་བཤེར་ཐོ། |
| bank reconciliation | དངུལ་ཁང་རྩིས་མཐུན་སྒྲིག |
| reconciliation | རྩིས་མཐུན་སྒྲིག |
| match / matched / unmatch / unmatched | ཟུང་སྒྲིག / ཟུང་སྒྲིག་ཟིན། / ཟུང་སྒྲིག་མེད་པར་གཏོང་། / ཟུང་སྒྲིག་མ་བྱས། |
| match group | ཟུང་སྒྲིག་ཚོ་ཁག |
| bank statement | དངུལ་ཁང་རྩིས་ཐོ། |
| bank line | དངུལ་ཁང་ཐོ་ཕྲེང་། |
| bank account | དངུལ་ཁང་རྩིས་ཁྲ། |
| counterparty | ཕ་རོལ་པོ། |
| accounts payable / receivable | སྤྲོད་དགོས་རྩིས། / ལེན་དགོས་རྩིས། |
| aging | དུས་ཡུན་དབྱེ་ཞིབ། |
| supplier / vendor | མཁོ་སྤྲོད་ཚོང་པ། |
| customer / client | ཚོང་མགྲོན། |
| invoice | ཚོང་འཛིན། |
| bill (supplier invoice) | མཁོ་སྤྲོད་ཚོང་འཛིན། |
| receipt | འཛིན་ཤོག |
| payment | དངུལ་སྤྲོད། |
| payment in / payment out | དངུལ་འབབ། / དངུལ་ཕྱིར་སྤྲོད། |
| payer / payee | དངུལ་སྤྲོད་མཁན། / དངུལ་ལེན་མཁན། |
| payment method | དངུལ་སྤྲོད་ཐབས་ལམ། |
| bank transfer / cheque / credit card / cash | དངུལ་ཁང་སྤོ་སྐྱེལ། / དངུལ་ཤོག / ཡིད་རྟོན་ཁཱ། / དངུལ་དངོས། |
| amount / total / net | དངུལ་གྲངས། / ཁྱོན་བསྡོམས། / གཙང་འབབ། |
| due date | སྤྲོད་དུས་ཚད། |
| reference | ཟུར་ཐོ་ཨང་། |
| currency / base currency | དངུལ་ལོར། / གཞི་རྩའི་དངུལ་ལོར། |
| exchange rate | དངུལ་བརྗེའི་ཚད། |
| exchange difference / gain / loss | དངུལ་བརྗེའི་ཁྱད་པར། / དངུལ་བརྗེའི་ཁེ་བཟང་། / དངུལ་བརྗེའི་གྱོང་ཁ། |
| exchange clearing account | དངུལ་བརྗེ་བར་བརྒྱུད་རྩིས་ཁོངས། |
| categorization rule / rule | དབྱེ་སྡེབ་སྒྲིག་གཞི། / སྒྲིག་གཞི། |
| pattern | དཔེ་གཞི། |
| split (across accounts) | བགོ་བཤའ། |
| fixed asset | བརྟན་འཇགས་རྒྱུ་ནོར། |
| depreciation / accumulated depreciation | རིན་ཆག / བསགས་པའི་རིན་ཆག |
| expense sheet | འགྲོ་སོང་ཐོ་ཤོག |
| expense (one claim line) | འགྲོ་སོང་། |
| reimbursement / reimburse | སླར་སྤྲོད། / སླར་སྤྲོད་བྱེད། |
| employee | ལས་བྱེད་པ། |
| approve / approved | ཆོག་མཆན་སྤྲོད། / ཆོག་མཆན་ཐོབ་ཟིན། |
| reject / rejected | ཁས་མི་ལེན། / ཁས་མ་བླངས། |
| submit / submitted | འབུལ། / ཕུལ་ཟིན། |
| tax | ཁྲལ། |
| VAT | རིན་འཕར་ཁྲལ། |
| GST / sales tax / consumption tax | ཟོང་དངོས་ཞབས་ཞུ་ཁྲལ། / བཙོང་ཁྲལ། / ཟད་སྤྱོད་ཁྲལ། |
| output VAT / input VAT | ཐོན་ཕྱོགས་རིན་འཕར་ཁྲལ། / འཇུག་ཕྱོགས་རིན་འཕར་ཁྲལ། |
| surcharge (on VAT) | ཁ་སྣོན་ཁྲལ། |
| corporate income tax (CIT) | ཁེ་ལས་ཡོང་འབབ་ཁྲལ། |
| individual income tax (IIT) | མི་སྒེར་ཡོང་འབབ་ཁྲལ། |
| profits tax (Hong Kong) | ཁེ་སྤོགས་ཁྲལ། |
| provisional / prepaid tax | སྔོན་སྤྲོད་ཁྲལ། |
| tax return / filing | ཁྲལ་ཞུ། |
| assessment notice | ཁྲལ་དཔྱད་བརྡ་ཐོ། |
| accrue / accrual entry | སྔོན་འཇོག / སྔོན་འཇོག་རྩིས་འགོད། |
| settle / settlement entry | རྩིས་སྒྲིལ། / རྩིས་སྒྲིལ་རྩིས་འགོད། |
| adjustments | ལེགས་སྒྲིག |
| assessable profit | ཁྲལ་འཇལ་དགོས་པའི་ཁེ་བཟང་། |
| template | མ་དཔེ། |
| company | ཀུང་སི། |
| legal name | ཁྲིམས་ལྡན་མིང་། |
| report | སྙན་ཐོ། |

## Documents, modules, people

| English | བོད་ཡིག |
|---|---|
| document | ཡིག་ཆ། |
| tag | རྟགས། |
| custom field | རང་སྒྲིག་ཡིག་ཁོངས། |
| correspondent | འབྲེལ་གཏུག་པ། |
| document type | ཡིག་ཆའི་རིགས། |
| storage path | ཉར་ཚགས་ལམ་ཐིག |
| workflow | ལས་རིམ། |
| archive | ཡིག་མཛོད། |
| business card | མིང་བྱང་། |
| extraction / extract | ཕྱིར་འདོན། |
| confidence | ཡིད་ཆེས་ཚད། |
| needs review / reviewed | ཞིབ་བཤེར་དགོས། / ཞིབ་བཤེར་བྱས་ཟིན། |
| anonymise / Anonymiser | མིང་གསང་། / མིང་གསང་ཆས། |
| personal details | སྒེར་གྱི་ཆ་འཕྲིན། |
| user / admin / group | བེད་སྤྱོད་མཁན། / དོ་དམ་པ། / ཚོགས་པ། |
| role / permission | གནས་ཚད། / དབང་ཚད། |
| viewer | ལྟ་མཁན། |

## Interface

| English | བོད་ཡིག |
|---|---|
| settings | སྒྲིག་འགོད། |
| dashboard | སྤྱི་མཐོང་ལྡེབ། |
| overview | སྤྱི་མཐོང་། |
| save | ཉར་ཚགས། |
| cancel | རྩིས་མེད། |
| delete | བསུབ་པ། |
| edit | ཞུ་དག |
| create / add | གསར་བཟོ། / སྣོན་པ། |
| search | འཚོལ་བཤེར། |
| filter / filters | འཚག / འཚག་མ། |
| export / import | ཕྱིར་གཏོང་། / ནང་འདྲེན། |
| upload / download | སྤར་བ། / ཕབ་ལེན། |
| apply | ལག་བསྟར། |
| confirm | གཏན་འཁེལ། |
| close / open | ཁ་རྒྱག / ཁ་ཕྱེ། |
| refresh / retry | སླར་གསོ། / བསྐྱར་ཚོད། |
| preview | སྔོན་ལྟ། |
| loading… | འདྲེན་བཞིན་པ།… |
| error / warning | ནོར་འཁྲུལ། / ཉེན་བརྡ། |
| status | གནས་སྟངས། |
| date | ཚེས་གྲངས། |
| description | འགྲེལ་བཤད། |
| category | རིགས་དབྱེ། |
| optional / required | འདེམས་ཆོག / ངེས་པར་དགོས། |
| all / none | ཡོངས། / མེད། |
| yes / no | ཡིན། / མིན། |
| next / previous | རྗེས་མ། / སྔོན་མ། |
