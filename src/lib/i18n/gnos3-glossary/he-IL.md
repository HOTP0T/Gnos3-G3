# Gnos3 — Hebrew (he-IL, עברית) glossary

Modern Israeli business Hebrew, the register of Israeli accounting and ERP software (Priority, חשבשבת) and of Israeli GAAP / IFRS terminology as used by רואי חשבון.

## Conventions

- **Register / address**: formal and gender-neutral. Never address the reader with a gendered imperative or pronoun (אתה / את, "בחר" / "בחרי"). Instructions use impersonal forms: "יש לבחור חשבון", "נא להזין סכום", "ניתן לייבא קובץ Excel". Messages about the system use the passive or a neutral subject: "החשבון נשמר", "לא נמצא חשבון".
- **Buttons, menu items and commands**: the action noun (שם פעולה), short and gender-neutral: שמירה, ביטול, מחיקה, עריכה, הוספה, ייצוא, ייבוא, העלאה, הורדה, החלה, אישור, סינון, חיפוש, רישום בספרים, יצירת פקודה. (The older Open WebUI / K4mi strings use the masculine imperative שמור / מחק; new and revised strings use the noun form.) Titles, tabs and column headers are nouns: הגדרות, דוחות, סטטוס.
- **Case**: Hebrew has no capitals. English ALL-CAPS statement totals (ASSETS, TOTAL) are written normally; emphasis comes from the UI.
- **Punctuation**: Latin punctuation, as in Israeli usage (period, comma, colon, question mark — no space before them). Acronyms and abbreviations take the Hebrew gershayim ״ (U+05F4) and geresh ׳ (U+05F3), never the ASCII " or ': מע״מ, ש״ח, מס׳, ח׳ / ז׳. "Report" is written דוח (the Academy spelling), plural דוחות. Quoted UI labels and names go in straight double quotes "…" ("{{name}}"). Keep the arrow "→" of menu paths (Settings → Countries = הגדרות → מדינות). Dash "—" as in English.
- **Placeholders, codes and product names** stay Latin and unchanged: {{count}}, {code}, <0>…</0>, Gnos3, K4mi, SmartOffice, Ollama, Open WebUI, Excel, PDF, CSV, XLSX, IBAN, EUR, HKD, ILS, MPF, %. The browser handles right-to-left layout; do not add direction marks (RLM / LRM).
- **Numbers and dates**: Western digits; the app formats amounts and dates through the UI locale (Israel: DD/MM/YYYY, decimal point, comma for thousands). Percent sign after the number (35%). Debit / credit column abbreviations: ח׳ / ז׳ (חובה / זכות).
- **Upload / download**: העלאה = upload, הורדה = download.
- **Void vs cancel**: ביטול = Cancel (closing a dialog); "ביטול פקודה" / "ביטול התשלום" (with the object named) = Void, so the two never read alike on one screen; voided = מבוטל / בוטלה.
- **Plurals and gender with numbers**: with a {{count}} placeholder prefer a construction that reads for every number and gender: "{{count}} פקודות", "פקודות: {{count}}". Singular templates ("{{count}} row") still use the plural form when the number may be 0.
- **Taxes named from a placeholder** ({{tax}} / {tax}: מע״מ, מס טובין ושירותים, מס חברות…) are written so the gender does not matter: put the placeholder after a noun ("דוח {{tax}}", "חשבונות {{tax}}") rather than agreeing an adjective with it.
- **e.g.** = לדוגמה; **i.e.** = כלומר; **etc.** = וכו׳.

## Accounting and finance

| English | Hebrew |
|---|---|
| account (ledger) | חשבון |
| account code / account name | קוד חשבון / שם חשבון |
| chart of accounts | מפתח חשבונות |
| control account (with sub-accounts) | חשבון מרכז |
| sub-account | תת-חשבון |
| detail / leaf account | חשבון סופי |
| journal entry / entry / transaction (GL) | פקודת יומן / פקודה |
| entry line | שורת פקודה |
| journal | יומן |
| general ledger | ספר ראשי (כרטסת) |
| sub-ledger | ספר עזר |
| trial balance | מאזן בוחן |
| balance sheet | מאזן |
| profit and loss / income statement | דוח רווח והפסד |
| statement of financial position (HK) | דוח על המצב הכספי |
| statement of profit or loss (HK) | דוח רווח או הפסד |
| assets / current / non-current | נכסים / שוטפים / לא שוטפים |
| liabilities / current / non-current | התחייבויות / שוטפות / לא שוטפות |
| equity | הון עצמי |
| retained earnings | עודפים (יתרת רווח) |
| revenue / income | הכנסות |
| expense (account type, P&L) | הוצאות |
| cost of sales / COGS | עלות המכר |
| gross profit / operating profit / net income | רווח גולמי / רווח תפעולי / רווח נקי |
| fiscal year / FY | שנת כספים / ש״כ |
| accounting period | תקופה חשבונאית |
| year to date (YTD) | מתחילת השנה |
| year-end closing | סגירת שנה |
| close / reopen a period | סגירה / פתיחה מחדש של תקופה |
| opening balance / closing balance | יתרת פתיחה / יתרת סגירה |
| debit / credit (DR / CR) | חובה / זכות (ח׳ / ז׳) |
| balance (of an account) | יתרה |
| draft | טיוטה |
| post / posted | רישום בספרים (לרשום בספרים) / נרשמה |
| book (an invoice), booking | רישום, רישום חשבונית בספרים |
| booking defaults | ברירות מחדל לרישום |
| void / voided | ביטול פקודה / מבוטלת |
| reversal (entry) | פקודת סטורנו |
| gap (line awaiting an account) | פער (שורה הממתינה לחשבון) |
| blocker | חסם |
| closing checklist | רשימת בדיקות לסגירה |
| invoice / bill (supplier invoice) | חשבונית / חשבונית ספק |
| receipt | קבלה |
| payment / payment in / payment out | תשלום / תקבול / תשלום יוצא |
| payer / payee | משלם / מוטב |
| payment method | אמצעי תשלום |
| bank transfer / check / credit card / cash | העברה בנקאית / שיק / כרטיס אשראי / מזומן |
| bank account | חשבון בנק |
| bank statement | דף חשבון בנק |
| bank line | תנועת בנק |
| bank reconciliation | התאמת בנקים |
| match / unmatch / matched | התאמה / ביטול התאמה / מותאם |
| match group | קבוצת התאמה |
| counterparty | צד נגדי |
| supplier / vendor | ספק |
| customer | לקוח |
| accounts payable (AP) | ספקים לתשלום (זכאים) |
| accounts receivable (AR) | לקוחות לגבייה (חייבים) |
| AP / AR aging | גיול ספקים / גיול לקוחות |
| company | חברה |
| legal entity name | שם משפטי |
| currency / base currency | מטבע / מטבע בסיס |
| exchange rate | שער חליפין |
| exchange difference / gain / loss | הפרשי שער / רווח משער / הפסד משער |
| exchange clearing account | חשבון מעבר להפרשי שער |
| clearing account | חשבון מעבר |
| override (company rate) | שער ייעודי |
| categorization rule | כלל סיווג |
| bank-line rule | כלל לתנועות בנק |
| pattern | דפוס |
| split (across accounts) | פיצול |
| fixed asset | רכוש קבוע |
| depreciation / accumulated depreciation | פחת / פחת נצבר |
| useful life / salvage value / book value | אורך חיים שימושי / ערך גרט / ערך בספרים |
| straight-line / declining balance | קו ישר / יתרה פוחתת |
| expense (an employee's claim) | הוצאה |
| expense sheet / expense claim | דוח הוצאות |
| expense receipt | קבלה (אסמכתה) |
| reimbursement | החזר הוצאות |
| employee | עובד |
| submit / approve / reject | הגשה / אישור / דחייה |
| VAT | מע״מ |
| GST / GST-HST / sales tax / consumption tax | מס טובין ושירותים (GST) / GST-HST / מס מכירה / מס צריכה |
| output VAT / input VAT | מע״מ עסקאות / מע״מ תשומות |
| VAT payable / VAT credit | מע״מ לתשלום / מע״מ להחזר |
| credit brought forward / carried forward | יתרת זכות מועברת / יתרת זכות להעברה |
| surcharge (China, on VAT) | היטל |
| corporate income tax (CIT) | מס חברות |
| individual income tax (IIT) | מס הכנסה ליחידים |
| profits tax (Hong Kong) | מס רווחים |
| provisional tax | מקדמות מס |
| prepaid tax (asset) | מס ששולם מראש |
| assessment notice / demand note | הודעת שומה / דרישת תשלום |
| tax return / filing | דוח מס / הגשה |
| accrual / accrual entry | הפרשה / פקודת הפרשה |
| settlement entry (VAT) | פקודת סילוק |
| settle (a filing) | סילוק |
| add-back / deduction | תוספת / ניכוי |
| assessable profit | הכנסה חייבת |
| losses brought forward | הפסדים מועברים |
| tax brackets / tiers | מדרגות מס |
| tax role mapping / mapped | מיפוי / ממופה |
| template | תבנית |
| needs review / mark reviewed | דורש בדיקה / סימון כנבדק |
| business card | כרטיס ביקור |
| anonymise / anonymiser | התממה / מתמם (Anonymiser) |

## Documents (K4mi)

| English | Hebrew |
|---|---|
| document | מסמך |
| tag | תגית |
| custom field | שדה מותאם אישית |
| correspondent | מכותב |
| document type | סוג מסמך |
| storage path | נתיב אחסון |
| workflow | זרימת עבודה |
| owner / permissions | בעלים / הרשאות |
| archive serial number (ASN) | מספר סידורי בארכיון |
| saved view | תצוגה שמורה |
| notes | הערות |
| trash | אשפה |

## UI words

| English | Hebrew |
|---|---|
| settings | הגדרות |
| dashboard | לוח בקרה |
| workspace | סביבת עבודה |
| save / cancel | שמירה / ביטול |
| delete / remove | מחיקה / הסרה |
| edit | עריכה |
| add / create | הוספה / יצירה |
| search / filter | חיפוש / סינון |
| export / import | ייצוא / ייבוא |
| upload / download | העלאה / הורדה |
| apply / confirm | החלה / אישור |
| close / back / next | סגירה / חזרה / הבא |
| preview / details | תצוגה מקדימה / פרטים |
| reset / clear | איפוס / ניקוי |
| refresh / retry | רענון / ניסיון חוזר |
| loading… | טוען… |
| error / warning | שגיאה / אזהרה |
| status | סטטוס |
| optional / required | אופציונלי / חובה |
| enabled / disabled | מופעל / מושבת |
| admin / superadmin | מנהל / מנהל־על |
| user / group / role | משתמש / קבוצה / תפקיד |
| report | דוח |
