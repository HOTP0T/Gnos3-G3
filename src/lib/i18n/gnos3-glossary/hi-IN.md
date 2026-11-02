# Gnos3 — Hindi (hi-IN) glossary

Translators of Gnos3, Finances, K4mi, Open WebUI and the expense app follow these terms so one word means one thing everywhere.

## Conventions

- **Register**: polite "आप" form throughout (never "तुम" / "तू"). Instructions and messages use the polite imperative: "चुनें", "दर्ज करें", "फिर से प्रयास करें".
- **Buttons**: short polite imperative, verb last: "सहेजें", "हटाएँ", "प्रविष्टि बनाएँ", "पोस्ट करें". Labels and column headings are nouns: "राशि", "तिथि", "स्थिति".
- **Sentence case** for English words kept inside Hindi text (product names stay as written: Gnos3, K4mi, SmartOffice, Ollama, Open WebUI, Excel, PDF, CSV). Currency codes (EUR, HKD), units and account codes stay as they are.
- **Punctuation**: a full sentence ends with the पूर्ण विराम "।"; "?" and "!" as in English; ":" after a label with no space before it; straight double quotes “…” (or "…") around quoted UI labels and names; "उदा." for "e.g."; "आदि" for "etc."; an ellipsis "…" stays.
- **Spelling**: use nukta where Hindi spells it (फ़ाइल, फ़िल्टर, दस्तावेज़, ज़रूरी, फ़ील्ड); chandrabindu in plural/imperative endings (हटाएँ, बनाएँ, प्रविष्टियाँ, परिसंपत्तियाँ); "कृपया" only where a request really needs it, not on every message.
- **Numbers and dates**: Western digits 0–9 (never Devanagari digits); amounts, dates and month names are formatted by the app (do not rewrite them in strings). Keep `{{placeholder}}` / `{placeholder}` and `<0>…</0>` tags exactly; move them to where Hindi word order needs them (Hindi is SOV: "{{count}} प्रविष्टियाँ पोस्ट की गईं").
- **Gender/agreement**: प्रविष्टि, इनवॉइस, अवधि, कंपनी, फ़ाइल, पंक्ति are feminine (प्रविष्टि पोस्ट की गई); खाता, दस्तावेज़, भुगतान, नियम, टैग are masculine (खाता बनाया गया). A `{tax}` / `{{tax}}` slot is treated as masculine (कर, वैट, जीएसटी): "{tax} देय है".
- **DR / CR** in column headings: "डेबिट" / "क्रेडिट" (short: "डे." / "क्रे."). Do not use "नाम / जमा": नाम also means "Name" on the same screens.
- **Void vs cancel**: Cancel (close a dialog) = "रद्द करें"; Void (an entry/match) = "निरस्त करें" / "निरस्त", so the two never read alike.
- **ALL-CAPS** statement totals: Devanagari has no capitals; write them normally (optionally in bold by the layout).

## Accounting and finance

| English | Hindi |
|---|---|
| account (ledger account) | खाता |
| account code / account name | खाता कोड / खाते का नाम |
| chart of accounts | खातों का चार्ट |
| chart template | चार्ट टेम्पलेट |
| control account | नियंत्रण खाता |
| sub-account | उप-खाता |
| detail / leaf account | विस्तृत खाता (अंतिम स्तर) |
| account type | खाता प्रकार |
| journal entry / entry / transaction (booked) | जर्नल प्रविष्टि / प्रविष्टि |
| entry line / line | प्रविष्टि पंक्ति / पंक्ति |
| journal | जर्नल |
| ledger | खाता बही |
| general ledger | सामान्य खाता बही |
| sub-ledger | सहायक खाता बही |
| trial balance | तलपट |
| balance sheet | तुलन पत्र |
| profit and loss / P&L / income statement | लाभ-हानि / लाभ-हानि विवरण |
| statement of financial position (HK) | वित्तीय स्थिति विवरण |
| statement of profit or loss (HK) | लाभ या हानि विवरण |
| assets / current / non-current | परिसंपत्तियाँ / चालू / गैर-चालू |
| liabilities | दायित्व |
| equity | इक्विटी |
| retained earnings | प्रतिधारित आय |
| revenue / income | राजस्व / आय |
| expense (account type, P&L) | व्यय |
| cost of sales | बिक्री की लागत |
| gross profit / net profit | सकल लाभ / शुद्ध लाभ |
| fiscal year / FY | वित्तीय वर्ष / वि.व. |
| year to date (YTD) | वर्ष में अब तक (YTD) |
| accounting period / period | लेखा अवधि / अवधि |
| close / reopen a period | अवधि बंद करें / फिर से खोलें |
| year-end closing | वर्षांत समापन |
| closing checklist | समापन जाँच-सूची |
| opening balance | प्रारंभिक शेष |
| closing balance | अंतिम शेष |
| balance (amount left) | शेष |
| debit / credit | डेबिट / क्रेडिट |
| draft | ड्राफ़्ट |
| post / posted | पोस्ट करें / पोस्ट की गई |
| void / voided | निरस्त करें / निरस्त |
| reversal (entry) | उलट प्रविष्टि |
| book (an invoice) / booking | दर्ज करना (बही में) / बुकिंग |
| booking defaults | डिफ़ॉल्ट बुकिंग खाते |
| gap (line awaiting an account) | लंबित पंक्ति (खाता बाकी) |
| blocker | अवरोध |
| invoice | इनवॉइस |
| bill (supplier invoice) | आपूर्तिकर्ता इनवॉइस |
| receipt | रसीद |
| payment | भुगतान |
| inbound / outbound payment | प्राप्त भुगतान / किया गया भुगतान |
| payment method | भुगतान का तरीका |
| bank transfer / cheque / credit card / cash | बैंक ट्रांसफ़र / चेक / क्रेडिट कार्ड / नकद |
| payer / payee | भुगतानकर्ता / प्राप्तकर्ता |
| supplier / vendor | आपूर्तिकर्ता |
| customer | ग्राहक |
| counterparty | प्रतिपक्ष |
| accounts payable / receivable | देय खाते / प्राप्य खाते |
| AP / AR aging | देय / प्राप्य आयु-विश्लेषण |
| bank account | बैंक खाता |
| bank statement | बैंक स्टेटमेंट |
| bank line / statement line | बैंक लाइन |
| bank reconciliation | बैंक समाधान |
| match / unmatch / matched | मिलान करें / मिलान हटाएँ / मिलान हुआ |
| match group | मिलान समूह |
| auto-match | स्वतः मिलान |
| exchange rate | विनिमय दर |
| exchange difference / gain / loss | विनिमय अंतर / विनिमय लाभ / विनिमय हानि |
| exchange clearing account | विनिमय समाशोधन खाता |
| base currency | आधार मुद्रा |
| currency | मुद्रा |
| rate override | विशेष दर |
| categorization rule | वर्गीकरण नियम |
| bank-line rule | बैंक लाइन नियम |
| split (across accounts) | विभाजन / विभाजित करें |
| fixed asset | स्थायी परिसंपत्ति |
| depreciation / accumulated depreciation | मूल्यह्रास / संचित मूल्यह्रास |
| useful life / salvage value / book value | उपयोगी जीवन / अवशिष्ट मूल्य / बही मूल्य |
| straight-line / declining balance | सीधी रेखा / ह्रासमान शेष |
| expense sheet | व्यय पत्रक |
| expenses (the expense-claims tab, `Expenses_tab`) | व्यय पत्रक |
| reimbursement | प्रतिपूर्ति |
| employee | कर्मचारी |
| approve / reject / submit | स्वीकृत करें / अस्वीकार करें / सबमिट करें |
| company | कंपनी |
| legal entity name | कानूनी नाम |
| template | टेम्पलेट |

## Tax

| English | Hindi |
|---|---|
| tax | कर |
| VAT / GST / sales tax / consumption tax | वैट / जीएसटी / बिक्री कर / उपभोग कर |
| output / input VAT | आउटपुट वैट / इनपुट वैट |
| VAT payable / VAT credit | देय वैट / वैट क्रेडिट |
| credit brought / carried forward | आगे लाया गया क्रेडिट / आगे ले जाया गया क्रेडिट |
| surcharge (China) | अधिभार |
| corporate income tax (CIT) | कॉर्पोरेट आयकर |
| individual income tax (IIT) | व्यक्तिगत आयकर |
| profits tax (Hong Kong) | लाभ कर |
| provisional tax | अनंतिम कर |
| prepaid tax | अग्रिम चुकाया गया कर |
| assessment notice / demand note | कर-निर्धारण नोटिस / माँग नोटिस |
| tax return / filing | कर रिटर्न / फ़ाइलिंग |
| accrual entry | उपार्जन प्रविष्टि |
| settlement entry / settle | निपटान प्रविष्टि / निपटान करें |
| add-back / deduction | वापस जोड़ / कटौती |
| tax adjustments | कर समायोजन |
| assessable profit | कर-योग्य लाभ |
| losses brought forward | आगे लाई गई हानियाँ |
| two-tier / tiered rates | दो-स्तरीय दरें / स्तरीय दरें |
| tax role mapping / mapped | मैपिंग / मैप किया गया |
| due date | देय तिथि |

## Documents (K4mi)

| English | Hindi |
|---|---|
| document | दस्तावेज़ |
| tag | टैग |
| custom field | कस्टम फ़ील्ड |
| correspondent | संवाददाता |
| document type | दस्तावेज़ प्रकार |
| storage path | स्टोरेज पाथ |
| workflow | वर्कफ़्लो |
| owner | स्वामी |
| note / notes | नोट / नोट्स |
| saved view | सहेजा गया दृश्य |
| business card | विज़िटिंग कार्ड |
| needs review / mark reviewed | समीक्षा आवश्यक / समीक्षित चिह्नित करें |
| extraction | निष्कर्षण |
| confidence | विश्वसनीयता |

## Interface

| English | Hindi |
|---|---|
| settings | सेटिंग्स |
| dashboard | डैशबोर्ड |
| save | सहेजें |
| cancel | रद्द करें |
| delete / remove | हटाएँ |
| edit | संपादित करें |
| create / add | बनाएँ / जोड़ें |
| search | खोजें |
| filter | फ़िल्टर |
| export / import | निर्यात करें / आयात करें |
| upload / download | अपलोड करें / डाउनलोड करें |
| apply | लागू करें |
| confirm | पुष्टि करें |
| close | बंद करें |
| refresh | रीफ़्रेश करें |
| retry | फिर से प्रयास करें |
| loading… | लोड हो रहा है… |
| error / warning | त्रुटि / चेतावनी |
| status | स्थिति |
| date / amount / total | तिथि / राशि / कुल |
| description | विवरण |
| reference | संदर्भ |
| user / group / role / permissions | उपयोगकर्ता / समूह / भूमिका / अनुमतियाँ |
| admin | व्यवस्थापक |
| preview | पूर्वावलोकन |
| optional / required | वैकल्पिक / आवश्यक |
| enabled / disabled | सक्षम / अक्षम |
| pending | लंबित |
| failed | विफल |
| anonymise / Anonymiser | अनामीकरण करें / अनामीकरण |
