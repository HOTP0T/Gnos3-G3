# Gnos3 — Azerbaijani (az-AZ, Latin script) glossary

## Conventions

- **Form of address**: formal "Siz". Sentences, hints and instructions use the polite imperative in -(y)in / -(y)ın / -(y)un / -(y)ün ("Hesabı seçin", "Məbləği daxil edin"); possessives use the "Sizin" form ("hesabınız", "şirkətiniz").
- **Buttons and menu items**: short bare imperative, as Open WebUI's az-AZ file already does ("Yadda saxla", "Ləğv et", "Sil", "Əlavə et", "Redaktə et", "Yazılışı keçir"). Column headers and labels are nouns ("Məbləğ", "Tarix", "Hesab").
- **Case**: sentence case — only the first word and proper names capitalised ("Hesablar planı", not "Hesablar Planı"). Azerbaijani letters: ə, ı, İ/i, ö, ü, ç, ş, ğ — always the correct ones, never ASCII substitutes; capital i with a dot is "İ" ("İdxal et").
- **Placeholders** ({{name}}, {name}): never attach a case suffix directly to a placeholder (the right vowel cannot be known). Rephrase so the placeholder stands in the nominative, or put a noun after it: "{{name}} şirkəti", "«{{name}}» silinəcək", "{{count}} yazılış".
- **Plurals**: after a number the noun stays singular ("3 hesab-faktura", "{{count}} sətir"), so English "(s)" forms need no plural ending.
- **Punctuation**: « » for quoted UI labels and names; no space before ":" "?" "!"; "—" kept where English uses it; "məs.:" for "e.g."; "və s." for "etc."; ellipsis "…".
- **Numbers and dates**: decimal comma, space as thousands separator (1 234,56); dates DD.MM.YYYY; "%" right after the number (20%); currency codes after the amount (1 000,00 AZN). The app formats numbers itself — do not change number formats inside strings.
- **Debit / credit abbreviations**: DR / CR → Dt / Kt (the local accounting abbreviations).
- **Product names stay**: Gnos3, K4mi, SmartOffice, Ollama, Open WebUI, Excel, PDF, CSV, currency codes, units. Country tax acronyms that have no local form stay in Latin (GST, HST, IRD, MPF).
- **Expense vs expenses tab**: "xərclər" = expense account type / P&L line; the expense-claims tab (key `Expenses_tab`) = "Xərc hesabatları".
- **Void vs cancel**: "Ləğv et" is the Cancel button; voiding an entry is "Yazılışı ləğv et", status "ləğv edilib". Reversal = "storno".
- **AI** = "Sİ" (süni intellekt): "Sİ təklifi", "Kateqoriyalaşdır (Sİ)", "Mühasibat Sİ-si".
- **Upload vs download**: upload = "yüklə", download = "endir" (never "yüklə" for both).
- **"Already paid"**: write "indiyədək ödənilmiş", not "artıq ödənilmiş" (which reads as "overpaid").
- **Tabs and screen names in running text** go in « » and take "bölməsi": «Yazılışlar» bölməsində, Ayarlar → Məzənnələr bölməsində.
- **Failure messages**: "… yüklənə bilmədi" / "… mümkün olmadı" (not "Uğursuz oldu").

## Accounting and finance

| English | Azərbaycanca |
|---|---|
| account (ledger) | hesab |
| account name | hesabın adı |
| account code | hesab kodu |
| account type | hesab növü |
| chart of accounts | hesablar planı |
| control account (with sub-accounts) | nəzarət hesabı |
| sub-account | subhesab |
| leaf / detail account | son səviyyəli hesab |
| journal | jurnal |
| journal entry / entry / transaction | mühasibat yazılışı / yazılış |
| entry line | yazılış sətri |
| ledger | kitab |
| general ledger | baş kitab |
| sub-ledger | köməkçi kitab |
| trial balance | sınaq balansı |
| balance sheet | mühasibat balansı |
| profit and loss / P&L / income statement | mənfəət və zərər hesabatı |
| statement of financial position (HK) | maliyyə vəziyyəti haqqında hesabat |
| statement of profit or loss (HK) | mənfəət və ya zərər haqqında hesabat |
| assets / liabilities / equity | aktivlər / öhdəliklər / kapital |
| current / non-current assets | qısamüddətli (dövriyyə) aktivlər / uzunmüddətli aktivlər |
| current / non-current liabilities | qısamüddətli öhdəliklər / uzunmüddətli öhdəliklər |
| retained earnings | bölüşdürülməmiş mənfəət |
| revenue / income | gəlir |
| other income | digər gəlirlər |
| cost of sales / COGS | satışın maya dəyəri |
| gross profit | ümumi mənfəət |
| operating profit | əməliyyat mənfəəti |
| net income / profit for the year | xalis mənfəət / ilin mənfəəti |
| administrative expenses / finance costs | inzibati xərclər / maliyyə xərcləri |
| expense (account type) | xərc |
| balance (of an account) | qalıq |
| opening balance | ilkin qalıq |
| closing balance | son qalıq |
| debit / credit | debet / kredit (Dt / Kt) |
| draft | qaralama |
| post / posted | keçir / keçirilib (keçirilmiş) |
| book (an invoice) / booking | uçota almaq / uçota alınma |
| booking defaults | standart uçot hesabları |
| void / voided | yazılışı ləğv et / ləğv edilib |
| reversal entry | storno yazılışı |
| accounting period / period | uçot dövrü / dövr |
| fiscal year (FY) | maliyyə ili (MI) |
| year to date (YTD) | ilin əvvəlindən |
| year-end closing | ilsonu bağlanış |
| close / reopen (a period) | bağla / yenidən aç |
| closing checklist | bağlanış yoxlamaları |
| blocker | maneə |
| gap (line awaiting an account) | boşluq (hesab gözləyən sətir) |
| bank reconciliation | bank üzləşdirməsi |
| reconcile | üzləşdir |
| match / unmatch / matched | uyğunlaşdır / uyğunlaşdırmanı ləğv et / uyğunlaşdırılıb |
| match group | uyğunlaşdırma qrupu |
| bank statement | bank çıxarışı |
| bank line (statement line) | bank sətri |
| bank account | bank hesabı |
| counterparty | kontragent |
| accounts payable / receivable | kreditor borcları / debitor borcları |
| AP / AR aging | kreditor / debitor borclarının müddətlər üzrə təhlili |
| supplier / vendor | təchizatçı |
| customer / client | müştəri |
| invoice | hesab-faktura |
| bill (supplier invoice) | təchizatçı hesab-fakturası |
| receipt | qəbz |
| payment | ödəniş |
| payment in / out | daxil olan ödəniş / çıxan ödəniş |
| payer / payee | ödəyici / benefisiar |
| payment method | ödəniş üsulu |
| bank transfer / check / card / cash | bank köçürməsi / çek / bank kartı / nağd |
| due date | ödəmə tarixi |
| amount / net / gross | məbləğ / xalis / ümumi (vergi daxil) |
| tax-inclusive | vergi daxil |
| currency / base currency | valyuta / əsas valyuta |
| exchange rate | məzənnə |
| exchange difference / gain / loss | məzənnə fərqi / məzənnə gəliri / məzənnə zərəri |
| exchange clearing account | məzənnə tranzit hesabı |
| rate override (company) | xüsusi məzənnə |
| categorization rule | kateqoriyalaşdırma qaydası |
| bank-line rule | bank sətri qaydası |
| pattern | nümunə |
| split (across accounts) | bölüşdür / bölgü |
| fixed asset | əsas vəsait |
| depreciation / accumulated depreciation | amortizasiya / yığılmış amortizasiya |
| useful life / salvage value / book value | faydalı istifadə müddəti / ləğvetmə dəyəri / balans dəyəri |
| asset register | əsas vəsaitlər reyestri |
| expense sheet | xərc hesabatı |
| reimbursement / reimburse | kompensasiya / kompensasiya et |
| employee | işçi |
| approve / reject / submit | təsdiqlə / rədd et / təqdim et |
| VAT | ƏDV (əlavə dəyər vergisi) |
| GST / sales tax / consumption tax | GST (mal və xidmət vergisi) / satış vergisi / istehlak vergisi |
| output / input VAT | hesablanmış ƏDV / əvəzləşdirilən ƏDV |
| VAT payable / VAT credit | ödəniləcək ƏDV / ƏDV krediti |
| credit brought / carried forward | əvvəlki dövrdən keçən kredit / növbəti dövrə keçən kredit |
| surcharge (on VAT) | əlavə yığım |
| corporate income tax (CIT) | korporativ mənfəət vergisi |
| profits tax (Hong Kong) | mənfəət vergisi |
| individual income tax (IIT) | fərdi gəlir vergisi |
| provisional tax | ilkin vergi |
| prepaid tax | əvvəlcədən ödənilmiş vergi |
| assessment notice / demand note | vergi bildirişi / ödəniş bildirişi |
| tax return / filing | bəyannamə |
| accrual entry | hesablama yazılışı |
| settlement entry / settle | hesablaşma yazılışı / hesablaş |
| add-back / deduction | əlavə edilən məbləğ / çıxılan məbləğ |
| tax adjustments | vergi düzəlişləri |
| assessable profit | vergiyə cəlb olunan mənfəət |
| losses brought forward | keçmiş illərin zərərləri |
| two-tier / tiered rates | iki pilləli dərəcə / pilləli dərəcələr |
| tax role / mapping / mapped | vergi rolu / əlaqələndirmə / əlaqələndirilib |
| template | şablon |
| company | şirkət |
| legal entity name | hüquqi şəxsin adı |

## Documents and modules

| English | Azərbaycanca |
|---|---|
| document | sənəd |
| tag | etiket |
| custom field | xüsusi sahə |
| correspondent | korrespondent |
| document type | sənəd növü |
| storage path | saxlama yolu |
| workflow | iş axını |
| inbox | gələnlər qutusu |
| owner | sahib |
| saved view | yadda saxlanmış görünüş |
| business card | vizit kartı |
| extraction | məlumatların çıxarılması |
| confidence | etibar dərəcəsi |
| needs review / mark reviewed | yoxlama tələb edir / yoxlanılmış kimi qeyd et |
| reprocess | yenidən emal et |
| anonymise / decrypt | anonimləşdir / şifrəni aç |
| knowledge base | bilik bazası |

## UI words

| English | Azərbaycanca |
|---|---|
| settings | ayarlar |
| dashboard | idarə paneli |
| save | yadda saxla |
| cancel | ləğv et |
| delete | sil |
| edit | redaktə et |
| search | axtar |
| filter | filtr |
| export / import | ixrac et / idxal et |
| upload / download | yüklə / endir |
| apply | tətbiq et |
| confirm | təsdiqlə |
| create / add / remove | yarat / əlavə et / çıxar |
| close | bağla |
| loading… | yüklənir… |
| error / warning | xəta / xəbərdarlıq |
| report | hesabat |
| status | status |
| permissions | icazələr |
| group | qrup |
