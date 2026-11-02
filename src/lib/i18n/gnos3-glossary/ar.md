# Gnos3 — Arabic (ar) glossary

Modern Standard Arabic, the register of Arab business and accounting software (SOCPA / IFRS Arabic terminology).

## Conventions

- **Register / address**: formal and impersonal. Prefer verbal nouns (المصدر) and passive or neutral phrasing over gendered imperatives: "يُرجى اختيار حساب" rather than "اختر حساباً". When an imperative cannot be avoided, use the generic masculine singular ("أضف"، "اختر"). Never colloquial.
- **Buttons and menu items**: the verbal noun, short: حفظ، إلغاء، حذف، تعديل، ترحيل القيد، إنشاء قيد، إضافة حساب. Titles and tabs: nouns (الإعدادات، التقارير).
- **Case**: Arabic has no capitals. English ALL-CAPS statement totals (ASSETS, TOTAL) are written normally; bold/weight comes from the UI.
- **Punctuation**: Arabic comma «،», semicolon «؛», question mark «؟». Full stop, colon «:», exclamation mark and the ellipsis «…» as in English. Quoted UI labels and names go in guillemets «…» (e.g. «{{name}}»). Keep the arrow "→" of menu paths as is (Settings → Countries = الإعدادات → الدول).
- **Placeholders, codes and product names** stay Latin and unchanged: {{count}}, {code}, <0>…</0>, Gnos3, K4mi, SmartOffice, Ollama, Open WebUI, Excel, PDF, CSV, XLSX, IBAN, EUR, HKD, %. The browser handles right-to-left layout; do not add direction marks.
- **Numbers and dates**: Western digits (0–9), as the app formats amounts and dates through the UI locale. Percent sign after the number (35%). Abbreviations for debit / credit columns: (مدين) / (دائن) written in full; where a column is tight, م / د.
- **Upload / download**: رفع = upload, تنزيل = download (never تحميل, which is ambiguous in Arabic UIs).
- **Void vs cancel**: إلغاء = Cancel (a dialog); إبطال = Void (an entry, a payment, a match group).
- **Plurals**: Arabic plural forms depend on the number; with a {{count}} placeholder use a neutral construction ("العدد: {{count}}"، "{{count}} من القيود"، "قيود ({{count}})") that reads for every number.
- **Taxes named from a placeholder** ({{tax}} / {tax}: ضريبة القيمة المضافة، ضريبة السلع والخدمات…) are treated as feminine nouns (ضريبة).

## Accounting and finance

| English | Arabic |
|---|---|
| account (ledger) | حساب |
| account code / account name | رمز الحساب / اسم الحساب |
| chart of accounts | دليل الحسابات |
| control account (with sub-accounts) | حساب إجمالي (رئيسي) |
| sub-account | حساب فرعي |
| detail / leaf account | حساب تفصيلي |
| journal entry / entry / transaction (GL) | قيد يومية / قيد |
| journal | دفتر اليومية |
| line (of an entry) | سطر / بند |
| general ledger | دفتر الأستاذ العام |
| trial balance | ميزان المراجعة |
| balance sheet | الميزانية العمومية |
| profit and loss / income statement | قائمة الأرباح والخسائر / قائمة الدخل |
| statement of financial position (HK) | قائمة المركز المالي |
| statement of profit or loss (HK) | قائمة الربح أو الخسارة |
| assets / current / non-current | الأصول / المتداولة / غير المتداولة |
| liabilities / current / non-current | الالتزامات / المتداولة / غير المتداولة |
| equity | حقوق الملكية |
| retained earnings | الأرباح المبقاة |
| revenue / income | الإيرادات |
| expenses (account type, P&L) | المصروفات |
| fiscal year / FY | السنة المالية / س.م |
| accounting period | الفترة المحاسبية |
| year to date (YTD) | منذ بداية السنة |
| opening balance / closing balance | الرصيد الافتتاحي / الرصيد الختامي |
| debit / credit (DR / CR) | مدين / دائن |
| draft | مسودة |
| post / posted | ترحيل / مُرحَّل |
| void / voided | إبطال / مُبطَل |
| reversal (entry) | قيد عكسي |
| book (an invoice) / booking | تسجيل (قيد) / القيد المحاسبي |
| booking engine / booking defaults | محرك القيود / الحسابات الافتراضية للقيود |
| gap (line awaiting an account) | بند معلّق |
| blocker | عائق |
| close / reopen a period | إقفال / إعادة فتح |
| year-end closing | إقفال نهاية السنة |
| closing checklist | قائمة فحوصات الإقفال |
| bank reconciliation | التسوية البنكية |
| match / unmatch / matched | مطابقة / إلغاء المطابقة / مُطابَق |
| match group | مجموعة مطابقة |
| bank statement | كشف الحساب البنكي |
| bank line | حركة بنكية |
| counterparty | الطرف المقابل |
| accounts payable / receivable | الذمم الدائنة / الذمم المدينة |
| AP / AR aging | أعمار الذمم الدائنة / أعمار الذمم المدينة |
| supplier / vendor | مورّد |
| customer / client | عميل |
| bill (supplier invoice) | فاتورة مورّد |
| invoice | فاتورة |
| receipt (expense proof) | إيصال |
| payment | دفعة |
| payment in / out (inbound / outbound) | مقبوضات / مدفوعات (وارد / صادر) |
| payer / payee | الدافع / المستفيد |
| payment method | طريقة الدفع |
| bank transfer / cheque / credit card / cash | تحويل بنكي / شيك / بطاقة ائتمان / نقدًا |
| currency / base currency | العملة / العملة الأساسية |
| exchange rate | سعر الصرف |
| exchange difference / gain / loss | فروق الصرف / أرباح فروق الصرف / خسائر فروق الصرف |
| exchange clearing account | حساب مقاصة الصرف |
| categorization rule | قاعدة تصنيف |
| pattern | نمط |
| split (across accounts) | توزيع |
| fixed asset | أصل ثابت |
| depreciation / accumulated depreciation | الإهلاك / مجمع الإهلاك |
| expense sheet (claim) | كشف مصروفات |
| expenses (the claims tab, `Expenses_tab`) | كشوف المصروفات |
| reimbursement | استرداد المصروفات |
| employee | موظف |
| approve / reject / submit | اعتماد / رفض / تقديم |
| VAT | ضريبة القيمة المضافة |
| GST / GST-HST / sales tax / consumption tax | ضريبة السلع والخدمات / ضريبة السلع والخدمات المنسّقة / ضريبة المبيعات / ضريبة الاستهلاك |
| output VAT / input VAT | ضريبة المخرجات / ضريبة المدخلات |
| VAT payable / VAT credit | ضريبة القيمة المضافة المستحقة / الرصيد الدائن للضريبة |
| corporate income tax (CIT) | ضريبة دخل الشركات |
| individual income tax (IIT) | ضريبة دخل الأفراد |
| profits tax (Hong Kong) | ضريبة الأرباح |
| provisional tax | الضريبة المؤقتة |
| prepaid tax (asset) | ضريبة مدفوعة مقدمًا |
| tax return / filing | الإقرار الضريبي |
| accrual entry | قيد الاستحقاق |
| settlement entry | قيد التسوية |
| tax computation adjustments | التعديلات الضريبية |
| assessable profit | الربح الخاضع للضريبة |
| mapping / mapped (tax role → account) | ربط / مربوط |
| template | قالب |
| company | شركة |
| business card | بطاقة عمل |
| needs review / mark reviewed | بحاجة إلى مراجعة / تعليم كمُراجَع |
| amount / total / subtotal | المبلغ / الإجمالي / المجموع الفرعي |
| due date / overdue | تاريخ الاستحقاق / متأخر السداد |

## Documents (K4mi)

| English | Arabic |
|---|---|
| document | مستند |
| tag | علامة |
| custom field | حقل مخصص |
| correspondent | جهة التراسل |
| document type | نوع المستند |
| storage path | مسار التخزين |
| owner | المالك |
| upload | رفع |
| workflow | سير العمل |
| reprocess | إعادة المعالجة |

## Interface

| English | Arabic |
|---|---|
| settings | الإعدادات |
| dashboard | لوحة التحكم |
| save | حفظ |
| cancel | إلغاء |
| delete | حذف |
| edit | تعديل |
| search | بحث |
| filter | تصفية |
| export / import | تصدير / استيراد |
| download | تنزيل |
| apply | تطبيق |
| confirm | تأكيد |
| loading… | جارٍ التحميل… |
| error / warning | خطأ / تحذير |
| status | الحالة |
| preview | معاينة |
| permissions | الصلاحيات |
| admin / superadmin | مسؤول / مسؤول أعلى |
| anonymise / anonymiser | إخفاء الهوية / أداة إخفاء الهوية (Anonymiser) |
