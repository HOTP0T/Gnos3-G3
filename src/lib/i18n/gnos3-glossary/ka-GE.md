# Gnos3 — Georgian (ka-GE, ქართული) glossary

## Conventions

- **Form of address**: formal "თქვენ". Sentences, hints and instructions use the polite plural imperative ("აირჩიეთ ანგარიში", "შეიყვანეთ თანხა", "დააჭირეთ…", "შეამოწმეთ…"); possessives use "თქვენი".
- **Buttons and menu items**: verbal noun (masdar), as Open WebUI's ka-GE file already does: "შენახვა", "გაუქმება", "წაშლა", "ჩასწორება", "დამატება", "ექსპორტი", "იმპორტი", "ატვირთვა", "ჩამოტვირთვა", "ჩანაწერის გატარება". Column headers and labels are nouns ("თანხა", "თარიღი", "ანგარიში"). Status words are participles ("გატარებული", "ანულირებული", "დამტკიცებული").
- **Case**: Georgian (Mkhedruli) has no capital letters; Latin acronyms and product names keep their own case.
- **Placeholders** ({{name}}, {name}): a case ending after a placeholder, number, acronym or Latin word is joined with a hyphen ("{{name}}-ის", "PDF-ში", "{count}-დან", "K4mi-ში"). Prefer rephrasing so the placeholder stands in the nominative or follows a noun ("კომპანია {{name}}", "„{{name}}“ წაიშლება").
- **Plurals**: after a number the noun stays singular ("3 ინვოისი", "{{count}} სტრიქონი"), so English singular / plural pairs often translate the same.
- **Punctuation**: Georgian quotation marks „…“ for quoted UI labels and names; no space before ":" "?" "!"; "—" kept where English uses it; "მაგ.:" for "e.g."; "და ა.შ." for "etc."; ellipsis "…".
- **Numbers and dates**: decimal comma, space as thousands separator (1 234,56); dates DD.MM.YYYY; "%" right after the number (18%); currency codes after the amount (1 000,00 GEL). The app formats numbers itself — do not change number formats inside strings.
- **Debit / credit abbreviations**: DR / CR → დტ / კტ.
- **Product names stay**: Gnos3, K4mi, SmartOffice, Ollama, Open WebUI, Excel, PDF, CSV, currency codes, units. Country tax acronyms with no Georgian form stay in Latin after a Georgian name (GST, HST, IRD, MPF).
- **Settings**: Open WebUI's file mixes "მორგება" and "პარამეტრები"; our screens use "პარამეტრები" (the standard word).
- **Expense vs expenses tab**: "ხარჯი / ხარჯები" = expense account type / P&L line; the expense-claims tab (key `Expenses_tab`) and expense sheets = "ხარჯების უწყისები".
- **Void vs cancel**: "გაუქმება" is the Cancel button; voiding an entry is "ანულირება", status "ანულირებული". Reversal = "სტორნო".
- **Entry vs post**: an entry is "ჩანაწერი" (journal entry = "სააღრიცხვო ჩანაწერი"); to post is "გატარება", posted = "გატარებული".

## Accounting and finance

| English | ქართული |
|---|---|
| account (ledger) | ანგარიში |
| account name | ანგარიშის დასახელება |
| account code | ანგარიშის კოდი |
| account type | ანგარიშის ტიპი |
| chart of accounts | ანგარიშთა გეგმა |
| control account (with sub-accounts) | შემაჯამებელი ანგარიში |
| sub-account | ქვეანგარიში |
| leaf / detail account | ბოლო დონის ანგარიში |
| journal | ჟურნალი |
| journal entry / entry / transaction | სააღრიცხვო ჩანაწერი / ჩანაწერი |
| entry line | ჩანაწერის სტრიქონი |
| post / posted | გატარება / გატარებული |
| draft | მონახაზი |
| void / voided | ანულირება / ანულირებული |
| reversal (entry) | სტორნო (სტორნო ჩანაწერი) |
| ledger | წიგნი |
| general ledger | მთავარი წიგნი |
| sub-ledger | დამხმარე წიგნი |
| trial balance | საცდელი ბალანსი |
| balance sheet | ბალანსი |
| profit and loss / P&L / income statement | მოგება-ზარალის ანგარიშგება |
| statement of financial position (HK) | ფინანსური მდგომარეობის ანგარიშგება |
| statement of profit or loss (HK) | მოგების ან ზარალის ანგარიშგება |
| assets / liabilities / equity | აქტივები / ვალდებულებები / კაპიტალი |
| current / non-current | მიმდინარე / გრძელვადიანი |
| revenue / income | შემოსავალი |
| expense (account type, P&L) | ხარჯი |
| cost of sales | გაყიდვების თვითღირებულება |
| gross profit / net income | მთლიანი მოგება / წმინდა მოგება |
| retained earnings | გაუნაწილებელი მოგება |
| opening balance / closing balance | საწყისი ნაშთი / საბოლოო ნაშთი |
| balance (of an account) | ნაშთი |
| debit / credit (DR / CR) | დებეტი / კრედიტი (დტ / კტ) |
| movement | ბრუნვა |
| fiscal year / FY | ფინანსური წელი / ფ.წ. |
| accounting period / period | საანგარიშო პერიოდი / პერიოდი |
| year to date (YTD) | წლის დასაწყისიდან |
| close / reopen (a period) | დახურვა / ხელახლა გახსნა |
| year-end closing | წლის დახურვა |
| closing checklist | დახურვის საკონტროლო სია |
| blocker | დამაბრკოლებელი პრობლემა |
| gap (line awaiting an account) | ხარვეზი (ანგარიშის მომლოდინე სტრიქონი) |
| booking / book (an invoice) | ასახვა / ასახვა აღრიცხვაში |
| booking defaults | ასახვის ნაგულისხმევი ანგარიშები |
| categorization rule | კატეგორიზაციის წესი |
| bank-line rule | საბანკო სტრიქონის წესი |
| pattern | ნიმუში |
| split (across accounts) | გადანაწილება |
| template | შაბლონი |
| company | კომპანია |
| legal entity name | იურიდიული დასახელება |
| invoice | ინვოისი |
| bill (supplier invoice) | მომწოდებლის ინვოისი |
| receipt | ქვითარი |
| payment / payment in / payment out | გადახდა / შემოსავალი გადახდა / გასავალი გადახდა |
| payer / payee | გადამხდელი / მიმღები |
| payment method | გადახდის მეთოდი |
| bank transfer / check / card / cash | საბანკო გადარიცხვა / ჩეკი / ბარათი / ნაღდი ფული |
| bank account | საბანკო ანგარიში |
| bank statement | საბანკო ამონაწერი |
| bank line | ამონაწერის სტრიქონი |
| bank reconciliation | საბანკო შეჯერება |
| match / unmatch / matched | შეჯერება / შეჯერების გაუქმება / შეჯერებული |
| match group | შეჯერების ჯგუფი |
| auto-match | ავტომატური შეჯერება |
| counterparty | კონტრაგენტი |
| supplier / vendor | მომწოდებელი |
| customer / client | კლიენტი |
| accounts payable / receivable (AP / AR) | კრედიტორული დავალიანება / დებიტორული დავალიანება |
| aging | ვადიანობის ანალიზი |
| expense sheet / reimbursement sheet | ხარჯების უწყისი |
| reimbursement | ანაზღაურება |
| employee | თანამშრომელი |
| approve / reject / submit | დამტკიცება / უარყოფა / გაგზავნა |
| currency / base currency | ვალუტა / საბაზისო ვალუტა |
| exchange rate | გაცვლითი კურსი |
| exchange difference / gain / loss | საკურსო სხვაობა / საკურსო მოგება / საკურსო ზარალი |
| exchange clearing account | საკურსო ტრანზიტული ანგარიში |
| fixed asset | ძირითადი საშუალება |
| depreciation / accumulated depreciation | ცვეთა / დაგროვილი ცვეთა |
| useful life / salvage value / book value | სასარგებლო მომსახურების ვადა / ნარჩენი ღირებულება / საბალანსო ღირებულება |

## Taxes

| English | ქართული |
|---|---|
| tax | გადასახადი |
| VAT | დღგ (დამატებული ღირებულების გადასახადი) |
| GST / GST-HST | საქონლისა და მომსახურების გადასახადი (GST) / GST-HST |
| sales tax / consumption tax | გაყიდვების გადასახადი / მოხმარების გადასახადი |
| output VAT / input VAT | დარიცხული დღგ / ჩასათვლელი დღგ |
| VAT payable / VAT credit | გადასახდელი დღგ / დღგ-ის ზედმეტობა |
| credit brought forward / carried forward | წინა პერიოდიდან გადმოტანილი ზედმეტობა / მომდევნო პერიოდზე გადასატანი ზედმეტობა |
| surcharge (China, on VAT) | დამატებითი მოსაკრებელი |
| corporate income tax (CIT) | მოგების გადასახადი |
| profits tax (Hong Kong) | მოგების გადასახადი (Profits Tax) |
| individual income tax (IIT) | საშემოსავლო გადასახადი |
| provisional tax | წინასწარი გადასახადი |
| prepaid tax | წინასწარ გადახდილი გადასახადი |
| assessment notice / demand note | საგადასახადო შეტყობინება / გადახდის მოთხოვნა |
| tax return / filing | დეკლარაცია |
| accrual entry | დარიცხვის ჩანაწერი |
| settlement entry / settle | ანგარიშსწორების ჩანაწერი / ანგარიშსწორება |
| add-back / deduction | დამატება / გამოქვითვა |
| assessable profit | დასაბეგრი მოგება |
| losses brought forward | გადმოტანილი ზარალი |
| tax role mapping / mapped | საგადასახადო როლის მიბმა / მიბმული |

## Documents, data and modules

| English | ქართული |
|---|---|
| document | დოკუმენტი |
| tag | ჭდე |
| custom field | მორგებული ველი |
| correspondent | კორესპონდენტი |
| document type | დოკუმენტის ტიპი |
| storage path | შენახვის გზა |
| workflow | სამუშაო პროცესი |
| owner | მფლობელი |
| business card | სავიზიტო ბარათი |
| needs review / mark reviewed | საჭიროებს გადამოწმებას / გადამოწმებულად მონიშვნა |
| extraction | ამოღება |
| confidence | სანდოობა |
| anonymise / anonymiser | ანონიმიზაცია / ანონიმიზატორი |

## UI words

| English | ქართული |
|---|---|
| settings | პარამეტრები |
| dashboard | საინფორმაციო დაფა |
| save | შენახვა |
| cancel | გაუქმება |
| delete / remove | წაშლა |
| edit | ჩასწორება |
| create / add | შექმნა / დამატება |
| search | ძებნა |
| filter | ფილტრი |
| export / import | ექსპორტი / იმპორტი |
| upload / download | ატვირთვა / ჩამოტვირთვა |
| apply | გამოყენება |
| confirm | დადასტურება |
| close | დახურვა |
| refresh | განახლება |
| loading… | იტვირთება… |
| error / warning | შეცდომა / გაფრთხილება |
| status | სტატუსი |
| date / amount / total | თარიღი / თანხა / სულ |
| description / notes | აღწერა / შენიშვნები |
| permissions / group / user | ნებართვები / ჯგუფი / მომხმარებელი |
| admin / superadmin | ადმინისტრატორი / სუპერადმინისტრატორი |
| required / optional | სავალდებულო / არასავალდებულო |
| preview | წინასწარი ნახვა |
| details | დეტალები |
