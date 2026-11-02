# Gnos3 — Persian (fa-IR) glossary

Formal written Persian (فارسی معیار), the register of Iranian business and accounting software (Sepidar, Hamkaran-style terminology; Iranian accounting standards for the accounting words).

## Conventions

- **Register / address**: formal, plural «شما». Polite requests use «لطفاً …» + subjunctive or a neutral phrasing ("لطفاً یک حساب انتخاب کنید"). Never colloquial forms (میشه، نمیشه، اینو).
- **Buttons and menu items**: short verbal nouns (اسم مصدر / بن فعل), no infinitive ending and no «کردن» when a short noun works: ذخیره، لغو، حذف، ویرایش، ایجاد سند، افزودن حساب، اعمال، تأیید، دانلود. Titles and tabs are nouns (تنظیمات، گزارش‌ها).
- **Case**: Persian has no capitals. English ALL-CAPS statement totals (ASSETS, TOTAL) are written normally.
- **Zero-width non-joiner (نیم‌فاصله, U+200C)**: always with می‌/نمی‌، ‌ها، ‌های، ‌ای، ‌تر، ‌ترین and in compounds: حساب‌ها، می‌شود، تطبیق‌داده‌شده، پیش‌نویس، به‌روزرسانی. Never a plain space and never glued.
- **Spelling**: Persian «ی» and «ک» (never Arabic ي / ك); «تأیید»، «مأخذ» with hamza; «به‌عنوان»، «بر اساس».
- **Punctuation**: Persian comma «،», semicolon «؛», question mark «؟». Full stop, colon «:», exclamation mark and the ellipsis «…» as in English. Quoted UI labels, names and placeholders go in guillemets «…» (e.g. «{{name}}»). Keep the arrow "→" of menu paths (Settings → Countries = تنظیمات → کشورها).
- **Placeholders, codes and product names** stay Latin and unchanged: {{count}}, {code}, <0>…</0>, Gnos3, K4mi, SmartOffice, Ollama, Open WebUI, Excel, PDF, CSV, XLSX, IBAN, EUR, HKD, MPF, %. The browser lays out right-to-left; do not add direction marks.
- **Numbers and dates**: Western digits (0–9) inside our strings, because amounts and dates arrive through placeholders formatted by the app; dates are Gregorian (no Jalali conversion). Gregorian month names: ژانویه، فوریه، مارس، آوریل، مه، ژوئن، ژوئیه، اوت، سپتامبر، اکتبر، نوامبر، دسامبر. Percent after the number (35%). Debit / credit column abbreviations: بد / بس.
- **Plurals**: Persian nouns stay singular after a number ("{{count}} سند"، "{{count}} حساب"), so the English singular and plural keys usually get the same translation.
- **Void vs cancel**: «لغو» = Cancel (a dialog, an action); «ابطال» = Void (an entry, a payment, a match group). Voided = باطل‌شده.
- **Document vs entry**: a K4mi document is «سند»; a journal entry is always «سند حسابداری» (or a compound that makes it clear: سند پیش‌نویس، سند افتتاحیه، سند اختتامیه). Never a bare «سند» for an entry where a K4mi document could also be meant.
- **Invoice vs bank statement**: invoice = «فاکتور»; «صورت‌حساب» is kept for the bank statement (صورت‌حساب بانکی), so the two never collide.
- **Taxes named from a placeholder** ({{tax}} / {tax}: مالیات بر ارزش افزوده، مالیات بر کالا و خدمات…): put the placeholder where a noun fits ("اظهارنامه {{tax}}"); Persian has no gender, so no agreement issues.

## Accounting and finance

| English | Persian |
|---|---|
| account (ledger) | حساب |
| account code / account name | کد حساب / نام حساب |
| chart of accounts | سرفصل حساب‌ها |
| control account (with sub-accounts) | حساب کنترل |
| sub-account | زیرحساب |
| detail / leaf account | حساب جزء (تفصیلی) |
| account type | نوع حساب |
| journal entry / entry (GL transaction) | سند حسابداری |
| journal entries | اسناد حسابداری |
| line (of an entry) | ردیف |
| journal | دفتر روزنامه |
| ledger | دفتر |
| general ledger | دفتر کل |
| sub-ledger | دفتر معین |
| trial balance | تراز آزمایشی |
| balance sheet | ترازنامه |
| profit and loss / income statement | صورت سود و زیان |
| statement of financial position (HK) | صورت وضعیت مالی |
| statement of profit or loss (HK) | صورت سود یا زیان |
| assets / current / non-current | دارایی‌ها / جاری / غیرجاری |
| liabilities / current / non-current | بدهی‌ها / جاری / غیرجاری |
| equity | حقوق مالکانه |
| revenue / income | درآمد |
| expense (account type, P&L) | هزینه |
| cost of sales | بهای تمام‌شده فروش |
| gross profit / net income | سود ناخالص / سود خالص |
| retained earnings | سود (زیان) انباشته |
| fiscal year / FY | سال مالی |
| accounting period / period | دوره مالی / دوره |
| year to date (YTD) | از ابتدای سال تاکنون |
| opening balance / opening entry | مانده اول دوره / سند افتتاحیه |
| closing balance / closing entry | مانده پایان دوره / سند اختتامیه |
| balance (of an account) | مانده |
| debit / credit (DR / CR) | بدهکار / بستانکار (بد / بس) |
| draft | پیش‌نویس |
| post / posted | قطعی کردن / قطعی‌شده |
| void / voided | ابطال / باطل‌شده |
| reversal (entry) | سند برگشتی |
| book (an invoice) / booking | ثبت / ثبت در دفاتر |
| booking defaults | پیش‌فرض‌های ثبت |
| year-end closing | بستن حساب‌های پایان سال |
| close / reopen a period | بستن / بازگشایی دوره |
| closing checklist | فهرست کنترل بستن دوره |
| blocker | مانع |
| gap (line awaiting an account) | ردیف معلق (در انتظار حساب) |
| bank reconciliation | مغایرت‌گیری بانکی |
| match / unmatch / matched | تطبیق / لغو تطبیق / تطبیق‌داده‌شده |
| match group | گروه تطبیق |
| bank statement | صورت‌حساب بانکی |
| bank line | ردیف بانکی |
| bank account | حساب بانکی |
| counterparty | طرف حساب |
| accounts payable / receivable (AP / AR) | حساب‌های پرداختنی / دریافتنی |
| AP / AR aging | گزارش سنی پرداختنی‌ها / دریافتنی‌ها |
| aging bucket / "Current" bucket | بازه سنی / سررسیدنشده |
| supplier / vendor | تأمین‌کننده |
| customer | مشتری |
| invoice | فاکتور |
| bill (supplier invoice) | فاکتور خرید |
| sales invoice | فاکتور فروش |
| receipt | رسید |
| payment | پرداخت |
| payment in / out (inbound / outbound) | دریافت / پرداخت |
| payer / payee | پرداخت‌کننده / ذی‌نفع |
| payment method | روش پرداخت |
| bank transfer / check / credit card / cash | انتقال بانکی / چک / کارت اعتباری / نقد |
| amount / total / net | مبلغ / جمع کل / خالص |
| currency / base currency | ارز / ارز پایه |
| exchange rate | نرخ ارز |
| exchange difference / gain / loss | تفاوت تسعیر ارز / سود تسعیر / زیان تسعیر |
| exchange clearing account | حساب واسط ارز |
| override (company rate) | نرخ اختصاصی |
| categorization rule | قاعده طبقه‌بندی |
| bank-line rule | قاعده ردیف بانکی |
| pattern | الگو |
| template | قالب |
| split (across accounts) | تفکیک |
| fixed asset | دارایی ثابت |
| depreciation / accumulated depreciation | استهلاک / استهلاک انباشته |
| useful life / salvage value / book value | عمر مفید / ارزش اسقاط / ارزش دفتری |
| straight-line / declining | خط مستقیم / نزولی |
| asset register | دفتر دارایی‌های ثابت |
| expense sheet | گزارش هزینه |
| expense receipt | رسید هزینه |
| reimbursement | بازپرداخت هزینه |
| employee | کارمند |
| approve / reject / submit | تأیید / رد / ارسال |
| company | شرکت |
| legal entity name | نام ثبتی شرکت |

## Taxes

| English | Persian |
|---|---|
| tax | مالیات |
| VAT / GST / sales tax / consumption tax | مالیات بر ارزش افزوده / مالیات بر کالا و خدمات / مالیات بر فروش / مالیات بر مصرف |
| output / input VAT | مالیات ارزش افزوده فروش / مالیات ارزش افزوده خرید |
| VAT payable / VAT credit | مالیات ارزش افزوده پرداختنی / اعتبار مالیات ارزش افزوده |
| credit brought / carried forward | اعتبار منتقل‌شده از دوره قبل / اعتبار قابل انتقال به دوره بعد |
| surcharge (China, on VAT) | عوارض الحاقی |
| corporate income tax (CIT) | مالیات بر درآمد شرکت‌ها |
| individual income tax (IIT) | مالیات بر درآمد اشخاص حقیقی |
| profits tax (Hong Kong) | مالیات بر سود |
| provisional tax | مالیات علی‌الحساب |
| prepaid tax (asset) | مالیات پیش‌پرداخت |
| assessment notice / demand note | برگ تشخیص / برگ مطالبه |
| tax return / filing | اظهارنامه مالیاتی |
| accrual entry (tax) | سند ذخیره مالیات |
| settlement entry / settle | سند تسویه / تسویه |
| add-back / deduction | افزودنی / کسرشدنی |
| tax computation adjustments | تعدیلات مالیاتی |
| assessable profit | سود مشمول مالیات |
| losses brought forward | زیان‌های سنواتی انتقالی |
| two-tier / tiered rates | نرخ دوپله‌ای / نرخ پلکانی |
| tax role mapping / mapped | نگاشت / نگاشت‌شده |
| due date | سررسید |

## Documents (K4mi)

| English | Persian |
|---|---|
| document | سند |
| tag | برچسب |
| custom field | فیلد سفارشی |
| correspondent | طرف مکاتبه |
| document type | نوع سند |
| storage path | مسیر ذخیره‌سازی |
| upload | بارگذاری |
| workflow | گردش کار |
| inbox | صندوق ورودی |
| owner | مالک |
| archive serial number | شماره سریال بایگانی |
| business card | کارت ویزیت |
| needs review / mark reviewed | نیازمند بازبینی / علامت‌گذاری به‌عنوان بازبینی‌شده |
| extraction | استخراج |
| reprocess | پردازش مجدد |
| confidence | میزان اطمینان |

## Interface

| English | Persian |
|---|---|
| settings | تنظیمات |
| dashboard | داشبورد |
| save / cancel / delete | ذخیره / لغو / حذف |
| edit / create / add / remove | ویرایش / ایجاد / افزودن / حذف |
| search / filter / sort | جستجو / فیلتر / مرتب‌سازی |
| export / import | خروجی گرفتن / وارد کردن |
| download | دانلود |
| apply / confirm / reset | اعمال / تأیید / بازنشانی |
| loading… | در حال بارگذاری… |
| error / warning | خطا / هشدار |
| refresh / retry | به‌روزرسانی / تلاش دوباره |
| preview / details | پیش‌نمایش / جزئیات |
| permissions / group / role | مجوزها / گروه / نقش |
| status / processing / failed | وضعیت / در حال پردازش / ناموفق |
| pending / approved / rejected | در انتظار / تأییدشده / ردشده |
| report / reports | گزارش / گزارش‌ها |
| optional / required | اختیاری / الزامی |
