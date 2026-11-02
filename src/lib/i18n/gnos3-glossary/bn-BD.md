# Gnos3 business modules — Bengali (bn-BD) glossary

Conventions:

- **Register**: formal "আপনি" throughout; polite imperative on buttons and actions (সংরক্ষণ করুন, দাখিলা তৈরি করুন, মুছে ফেলুন). Short noun labels stay nouns (অনুসন্ধান, ফিল্টার, সেটিংস).
- **Spelling**: standard Bangla Academy spelling (ব্যবহারকারী, not ব্যাবহারকারী; কোম্পানি; অ্যাকাউন্ট only when a login account is meant — a ledger account is always হিসাব).
- **Punctuation**: a full sentence ends with the দাঁড়ি "।"; labels, buttons and fragments get no full stop. "?" "!" ":" as in English, no space before them. Quoted UI labels and names in “ ” (curly double quotes). Ellipsis "…" for "loading…" style messages. Em dash "—" kept where English uses it.
- **Numbers and dates**: keep Western digits (0–9) as the app formats numbers, amounts and dates through placeholders; do not convert to Bengali digits inside strings, so typed figures and formatted figures match. Currency codes (BDT, USD, EUR, HKD) stay as codes. Abbreviations: DR / CR → ডে / ক্রে; e.g. → যেমন; YTD → বছরের শুরু থেকে; FY → অর্থবছর.
- **Plural**: Bengali marks plurals lightly (-সমূহ / -গুলি only where needed; a number already implies plural: "{{count}}টি ইনভয়েস"). Use the classifier টি after counts of things ("{{count}}টি লাইন").
- **Product names stay as written**: Gnos3, K4mi, SmartOffice, Finances (the app's own name, may be glossed "Finances (আর্থিক বিশ্লেষণ)" once), Ollama, Open WebUI, Excel, PDF, CSV, MPF, IRD.
- Taxes are named from the tax kind, never the country's label: `{{tax}}` / `{tax}` may be ভ্যাট, জিএসটি, বিক্রয় কর… write templates so the name reads naturally at the start or in parentheses.

## Accounting and finance

| English | বাংলা |
|---|---|
| account (ledger) | হিসাব |
| account type | হিসাবের ধরন |
| chart of accounts | হিসাবের তালিকা |
| control account | নিয়ন্ত্রণ হিসাব |
| sub-account | উপ-হিসাব |
| journal | জাবেদা |
| journal entry / entry | জাবেদা দাখিলা / দাখিলা |
| ledger | খতিয়ান |
| general ledger | সাধারণ খতিয়ান |
| trial balance | রেওয়ামিল |
| balance sheet | উদ্বৃত্তপত্র |
| statement of financial position | আর্থিক অবস্থার বিবরণী |
| profit and loss / income statement | লাভ-ক্ষতি বিবরণী |
| assets / current / non-current | সম্পদ / চলতি / অ-চলতি |
| liabilities | দায় |
| equity | মালিকানা স্বত্ব |
| revenue / income | আয় |
| expense (account type, P&L) | ব্যয় |
| cost of sales | বিক্রীত পণ্যের ব্যয় |
| gross profit / net income | মোট মুনাফা / নিট মুনাফা |
| retained earnings | সংরক্ষিত আয় |
| fiscal year | অর্থবছর |
| accounting period / period | হিসাবকাল |
| year-end closing | বছর শেষের সমাপনী |
| close / reopen (a period) | বন্ধ করুন / পুনরায় খুলুন |
| closing checklist | সমাপনী যাচাই তালিকা |
| opening balance | প্রারম্ভিক জের |
| closing balance | সমাপনী জের |
| balance | জের |
| debit / credit | ডেবিট / ক্রেডিট |
| draft | খসড়া |
| post / posted | পোস্ট করুন / পোস্টকৃত |
| book (an invoice) / booking | হিসাবভুক্ত করুন / হিসাবভুক্তি |
| booking defaults | ডিফল্ট হিসাবভুক্তি |
| void / voided | অকার্যকর করুন / অকার্যকর (never বাতিল, which is Cancel) |
| reversal entry | বিপরীত দাখিলা |
| gap (line awaiting an account) | অমীমাংসিত লাইন |
| blocker | বাধা |
| amount | পরিমাণ |
| base currency | মূল মুদ্রা |
| currency | মুদ্রা |
| exchange rate | বিনিময় হার |
| exchange gain / loss / difference | বিনিময় লাভ / বিনিময় ক্ষতি / বিনিময় পার্থক্য |
| exchange clearing account | বিনিময় ক্লিয়ারিং হিসাব |
| invoice | ইনভয়েস |
| bill (supplier invoice) | সরবরাহকারীর বিল |
| receipt | রসিদ |
| payment | পরিশোধ |
| payment method | পরিশোধের পদ্ধতি |
| bank transfer / cheque / credit card / cash | ব্যাংক ট্রান্সফার / চেক / ক্রেডিট কার্ড / নগদ |
| payer / payee | পরিশোধকারী / প্রাপক |
| supplier / vendor | সরবরাহকারী |
| customer / client | গ্রাহক |
| counterparty | প্রতিপক্ষ |
| accounts payable / receivable | প্রদেয় হিসাব / প্রাপ্য হিসাব |
| aging | মেয়াদভিত্তিক বিশ্লেষণ |
| bank statement | ব্যাংক বিবরণী |
| bank line | ব্যাংক লাইন |
| bank reconciliation | ব্যাংক মিলকরণ |
| match / unmatch / matched | মেলান / মিল বাতিল করুন / মেলানো |
| categorization rule | শ্রেণিবিন্যাস নিয়ম |
| split (across accounts) | ভাগ করুন / বিভাজন |
| fixed asset | স্থায়ী সম্পদ |
| depreciation / accumulated depreciation | অবচয় / পুঞ্জীভূত অবচয় |
| useful life / salvage value / book value | ব্যবহারযোগ্য আয়ু / অবশিষ্ট মূল্য / বই মূল্য |
| expense sheet | খরচ বিবরণী |
| expenses (claims tab, `Expenses_tab`) | খরচের দাবি |
| reimbursement | খরচ ফেরত |
| approve / reject / submit | অনুমোদন করুন / প্রত্যাখ্যান করুন / জমা দিন |
| company | কোম্পানি |
| adjustment | সমন্বয় |
| VAT / GST / sales tax / consumption tax | ভ্যাট / জিএসটি / বিক্রয় কর / ভোগ কর |
| output VAT / input VAT | উৎপাদ ভ্যাট / উপকরণ ভ্যাট |
| VAT payable / VAT credit | প্রদেয় ভ্যাট / ভ্যাট ক্রেডিট |
| credit brought / carried forward | পূর্ববর্তী জের টানা ক্রেডিট / পরবর্তী জের ক্রেডিট |
| surcharge | সারচার্জ |
| corporate income tax (CIT) | কর্পোরেট আয়কর |
| individual income tax (IIT) | ব্যক্তিগত আয়কর |
| profits tax (Hong Kong) | মুনাফা কর |
| provisional tax | অগ্রিম কর |
| prepaid tax | অগ্রিম পরিশোধিত কর |
| withholding | উৎসে কর কর্তন |
| tax return / filing | কর রিটার্ন |
| assessment notice / demand note | কর নির্ধারণী নোটিশ / দাবিনামা |
| assessable profit | করযোগ্য মুনাফা |
| losses brought forward | পূর্ববর্তী বছরের ক্ষতি |
| accrual (entry) | বকেয়া (দাখিলা) |
| settlement / settle | নিষ্পত্তি / নিষ্পত্তি করুন |
| mapping / mapped (tax role → account) | নির্ধারণ / নির্ধারিত |

## Documents and modules

| English | বাংলা |
|---|---|
| document | ডকুমেন্ট |
| tag | ট্যাগ |
| custom field | কাস্টম ফিল্ড |
| correspondent | প্রেরক |
| document type | ডকুমেন্টের ধরন |
| storage path | সংরক্ষণ পথ |
| workflow | ওয়ার্কফ্লো |
| business card | ভিজিটিং কার্ড |
| extraction / extract | তথ্য নিষ্কাশন / নিষ্কাশন করুন |
| confidence | আস্থার মান |
| needs review / mark reviewed | পর্যালোচনা প্রয়োজন / পর্যালোচিত হিসেবে চিহ্নিত করুন |
| reprocess | পুনরায় প্রক্রিয়া করুন |
| anonymise / anonymiser | বেনামী করুন / বেনামীকরণ |
| knowledge base | জ্ঞানভান্ডার |

## Interface words

| English | বাংলা |
|---|---|
| settings | সেটিংস |
| dashboard | ড্যাশবোর্ড |
| save | সংরক্ষণ করুন |
| cancel | বাতিল |
| delete | মুছে ফেলুন |
| edit | সম্পাদনা করুন |
| create / add | তৈরি করুন / যোগ করুন |
| remove | সরান |
| search | অনুসন্ধান |
| filter | ফিল্টার |
| export / import | রপ্তানি করুন / আমদানি করুন |
| upload / download | আপলোড করুন / ডাউনলোড করুন |
| apply | প্রয়োগ করুন |
| confirm | নিশ্চিত করুন |
| error / warning | ত্রুটি / সতর্কতা |
| user / group / permission | ব্যবহারকারী / গ্রুপ / অনুমতি |
| admin / superadmin | অ্যাডমিন / সুপার অ্যাডমিন |
| optional / required | ঐচ্ছিক / আবশ্যক |
