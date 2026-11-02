# Gnos3 business modules — Thai (th-TH) glossary

## Conventions

- **Register**: formal, neutral business Thai as used by Thai accounting software (PEAK, FlowAccount, Express). No polite particles (ครับ / ค่ะ / นะ). Address the reader as "คุณ" only when a sentence needs a subject; prefer impersonal phrasing ("ยังไม่มีบริษัท", "การดำเนินการนี้ไม่สามารถย้อนกลับได้"). Requests start with "กรุณา" ("กรุณาเลือกบริษัท").
- **Buttons and menu actions**: bare verb + object, short: "บันทึก", "ลบ", "สร้างรายการบันทึกบัญชี", "อัปโหลดไฟล์", "นำตัวกรองไปใช้". Progress states: "กำลัง…" + "…" ("กำลังโหลด…", "กำลังบันทึก…"). Done states: verb + "แล้ว" ("บันทึกแล้ว", "ผ่านรายการแล้ว"). Titles and labels are noun phrases ("รายการใหม่", "การตั้งค่าบริษัท").
- **Case**: Thai has no letter case. English acronyms and product names keep their own case (VAT, AI, Gnos3). ALL-CAPS statement totals become plain Thai (no special marking).
- **Spacing and punctuation**: no spaces between Thai words; a single space separates clauses / sentences and surrounds Latin words, numbers and placeholders when it helps reading ("{{count}} รายการ", "ไฟล์ Excel"). Thai does **not** end sentences with "." — drop the final full stop of English sentences (keep "?" when it is a question to the user, and ":" before a value). Quoted UI labels and names in “…”. Ellipsis "…". "e.g." → "เช่น", "i.e." → "คือ", "etc." → "ฯลฯ", "vs." → "เทียบกับ". The em dash "—" may be kept between clauses or replaced by a space.
- **Numbers and dates**: Arabic (Western) digits, never Thai digits; decimal point and thousands comma (1,234.56); percent without a space (7%). The app shows Gregorian years (ค.ศ.) as stored; never convert to the Buddhist era (พ.ศ.) in strings. Month and weekday names come from the locale, not from these strings.
- **Plurals**: Thai does not inflect; singular and plural English keys get the same Thai text, with a classifier after the number: "{{count}} รายการ" (entries, lines, items), "{{count}} ใบ" (invoices, receipts, sheets), "{{count}} บัญชี" (accounts), "{{count}} บริษัท", "{{count}} ไฟล์", "{{count}} แถว" (rows), "{{count}} คน" (people).
- **DR / CR** → **Dr / Cr** in narrow column headers (as Thai accountants write them); "เดบิต" / "เครดิต" written out elsewhere.
- **Placeholders** ({{name}}, {name}, <0>, <1/>) stay exactly as given; Thai word order may move them, never drop or rename them. A `{{tax}}` / `{tax}` holding a tax name (ภาษีมูลค่าเพิ่ม, GST, ภาษีเงินได้นิติบุคคล…) is used as a noun: "แบบยื่น{{tax}}", "{{tax}} ซื้อ" → prefer "ภาษีซื้อ ({{tax}})" when the tax name is generic.
- **Product names stay**: Gnos3, K4mi, SmartOffice, Ollama, Open WebUI, Excel, PDF, CSV, MPF, ICMS, IBAN, currency codes, units.
- Loanwords written the Thai way (Royal Institute style): แดชบอร์ด, แท็ก, ไฟล์, อัปโหลด, ดาวน์โหลด, เวิร์กโฟลว์, โมเดล, เทมเพลต is **not** used — template = "แม่แบบ".

## Accounting and finance

| English | Thai (th-TH) |
|---|---|
| account (ledger account, `Account_gnos3`) | บัญชี |
| account (user login) | บัญชีผู้ใช้ |
| account code / account name | รหัสบัญชี / ชื่อบัญชี |
| account type | ประเภทบัญชี |
| chart of accounts | ผังบัญชี |
| control account (with sub-accounts) | บัญชีคุม |
| sub-account | บัญชีย่อย |
| detail / leaf account | บัญชีระดับย่อยสุด |
| journal entry / entry / transaction (books) | รายการบันทึกบัญชี (short: รายการบัญชี) |
| line (of an entry) | บรรทัดรายการ |
| journal | สมุดรายวัน |
| general ledger / ledger | บัญชีแยกประเภททั่วไป / บัญชีแยกประเภท |
| sub-ledger | บัญชีแยกประเภทย่อย |
| trial balance | งบทดลอง |
| balance sheet | งบแสดงฐานะการเงิน |
| profit and loss / income statement / P&L | งบกำไรขาดทุน |
| statement of financial position (HK) | งบแสดงฐานะการเงิน |
| statement of profit or loss (HK) | งบกำไรขาดทุน |
| assets / liabilities / equity | สินทรัพย์ / หนี้สิน / ส่วนของเจ้าของ |
| current / non-current assets | สินทรัพย์หมุนเวียน / สินทรัพย์ไม่หมุนเวียน |
| current / non-current liabilities | หนี้สินหมุนเวียน / หนี้สินไม่หมุนเวียน |
| revenue / income | รายได้ |
| expense (account type, P&L) | ค่าใช้จ่าย |
| cost of sales / COGS | ต้นทุนขาย |
| gross profit / operating profit / net income | กำไรขั้นต้น / กำไรจากการดำเนินงาน / กำไรสุทธิ |
| retained earnings | กำไรสะสม |
| fiscal year / FY | ปีบัญชี |
| accounting period / period | งวดบัญชี / งวด |
| year to date (YTD) | สะสมตั้งแต่ต้นปี (YTD) |
| opening balance | ยอดยกมา |
| closing / ending balance | ยอดคงเหลือปลายงวด |
| beginning / ending (statement columns) | ต้นงวด / ปลายงวด |
| movement | ความเคลื่อนไหว |
| debit / credit | เดบิต / เครดิต |
| balance (of an account) | ยอดคงเหลือ |
| balanced / unbalanced | สมดุล / ไม่สมดุล |
| draft | ฉบับร่าง |
| post / posted | ผ่านรายการ / ผ่านรายการแล้ว |
| book (an invoice) / booking | บันทึกบัญชี / การบันทึกบัญชี |
| booking defaults | ค่าเริ่มต้นการบันทึกบัญชี |
| void / voided | ยกเลิกรายการ / ยกเลิกแล้ว (never plain "ยกเลิก" on the Void button: that is Cancel) |
| reversal (entry) | รายการกลับบัญชี |
| close / reopen a period | ปิดงวด / เปิดงวดอีกครั้ง |
| year-end closing | การปิดบัญชีสิ้นปี |
| closing checklist | รายการตรวจสอบก่อนปิดงวด |
| blocker | ประเด็นที่ต้องแก้ก่อน |
| gap (line awaiting an account) | รายการที่ยังไม่ระบุบัญชี |
| bank reconciliation | การกระทบยอดธนาคาร |
| reconcile / reconciled | กระทบยอด / กระทบยอดแล้ว |
| match / unmatch / matched | จับคู่ / ยกเลิกการจับคู่ / จับคู่แล้ว |
| match group | กลุ่มการจับคู่ |
| bank statement | รายการเดินบัญชีธนาคาร (สเตทเมนต์) |
| bank line | รายการธนาคาร |
| bank account | บัญชีธนาคาร |
| counterparty | คู่ค้า |
| accounts payable / receivable | เจ้าหนี้การค้า / ลูกหนี้การค้า |
| AP / AR aging | อายุเจ้าหนี้ / อายุลูกหนี้ |
| supplier / vendor | ผู้ขาย |
| customer / client | ลูกค้า |
| invoice | ใบแจ้งหนี้ |
| tax invoice | ใบกำกับภาษี |
| bill (supplier invoice) | ใบแจ้งหนี้ผู้ขาย |
| receipt | ใบเสร็จรับเงิน (expense app: ใบเสร็จ) |
| payment / payment in / payment out | การชำระเงิน / รับเงิน / จ่ายเงิน |
| payer / payee | ผู้จ่ายเงิน / ผู้รับเงิน |
| payment method | วิธีการชำระเงิน |
| bank transfer / cheque / credit card / cash | โอนเงินผ่านธนาคาร / เช็ค / บัตรเครดิต / เงินสด |
| due date / overdue | วันครบกำหนด / เกินกำหนด |
| currency / base currency | สกุลเงิน / สกุลเงินหลัก |
| exchange rate | อัตราแลกเปลี่ยน |
| exchange difference / gain / loss | ผลต่างจากอัตราแลกเปลี่ยน / กำไรจากอัตราแลกเปลี่ยน / ขาดทุนจากอัตราแลกเปลี่ยน |
| exchange clearing account | บัญชีพักอัตราแลกเปลี่ยน |
| override (company rate) | อัตราเฉพาะบริษัท |
| categorization rule | กฎการจัดประเภทบัญชี |
| bank-line rule | กฎรายการธนาคาร |
| split (across accounts) | แยกรายการ / การแยกรายการ |
| fixed asset | สินทรัพย์ถาวร |
| depreciation / accumulated depreciation | ค่าเสื่อมราคา / ค่าเสื่อมราคาสะสม |
| useful life / salvage value / book value | อายุการใช้งาน / มูลค่าซาก / มูลค่าตามบัญชี |
| straight-line / declining balance | วิธีเส้นตรง / วิธียอดลดลง |
| expense sheet | ใบเบิกค่าใช้จ่าย |
| expenses (the expense-claims tab, `Expenses_tab`) | การเบิกค่าใช้จ่าย |
| reimbursement / reimburse | การเบิกคืนเงิน / เบิกคืน |
| employee | พนักงาน |
| approve / reject / submit | อนุมัติ / ปฏิเสธ / ส่ง |
| company / legal name | บริษัท / ชื่อนิติบุคคล |
| template | แม่แบบ |

## Taxes

| English | Thai (th-TH) |
|---|---|
| VAT | ภาษีมูลค่าเพิ่ม (VAT) |
| GST / GST-HST / sales tax / consumption tax | ภาษีสินค้าและบริการ (GST) / GST-HST / ภาษีการขาย / ภาษีการบริโภค |
| output / input VAT | ภาษีขาย / ภาษีซื้อ |
| VAT payable / VAT credit | ภาษีมูลค่าเพิ่มที่ต้องชำระ / ภาษีมูลค่าเพิ่มที่ชำระไว้เกิน |
| credit brought / carried forward | เครดิตภาษียกมา / เครดิตภาษียกไป |
| surcharge (China, on VAT) | ภาษีเพิ่มเติม |
| corporate income tax (CIT) | ภาษีเงินได้นิติบุคคล |
| individual income tax (IIT) | ภาษีเงินได้บุคคลธรรมดา |
| withholding tax | ภาษีหัก ณ ที่จ่าย |
| profits tax (Hong Kong) | ภาษีกำไร (Profits Tax) |
| provisional tax | ภาษีชำระล่วงหน้า |
| prepaid tax (asset) | ภาษีจ่ายล่วงหน้า |
| assessment notice / demand note | หนังสือแจ้งการประเมินภาษี / หนังสือแจ้งให้ชำระภาษี |
| tax return / filing | แบบแสดงรายการภาษี / การยื่นแบบ |
| accrual entry (tax) | รายการตั้งค้างจ่าย |
| settlement entry (VAT) | รายการปิดบัญชีภาษี |
| settle (a filing) | ชำระภาษี |
| add-back / deduction | รายการบวกกลับ / รายการหักออก |
| adjusted / assessable profit | กำไรหลังปรับปรุง / กำไรสุทธิทางภาษี |
| losses brought forward | ผลขาดทุนสะสมยกมา |
| tax role mapping | การกำหนดบัญชีภาษี |
| tax office | กรมสรรพากร / หน่วยงานภาษี |

## Documents (K4mi) and modules

| English | Thai (th-TH) |
|---|---|
| document | เอกสาร |
| tag | แท็ก |
| custom field | ฟิลด์กำหนดเอง |
| correspondent | ผู้เขียน (K4mi's existing word) |
| document type | ประเภทเอกสาร |
| storage path | พาธจัดเก็บ |
| archive serial number (ASN) | รหัสการจัดเก็บถาวร (ASN) |
| owner | เจ้าของ |
| workflow | เวิร์กโฟลว์ |
| saved view | มุมมองที่บันทึกไว้ |
| inbox | กล่องขาเข้า |
| business card | นามบัตร |
| needs review / mark reviewed | รอตรวจสอบ / ทำเครื่องหมายว่าตรวจสอบแล้ว |
| extraction | การดึงข้อมูล |
| confidence | ความเชื่อมั่น |
| anonymise / anonymiser | ปกปิดข้อมูลส่วนบุคคล / ตัวปกปิดข้อมูล (Anonymiser) |
| personal details | ข้อมูลส่วนบุคคล |

## UI words (from Open WebUI's Thai catalog where it has them)

| English | Thai (th-TH) |
|---|---|
| settings | การตั้งค่า |
| dashboard | แดชบอร์ด |
| save / saved | บันทึก / บันทึกแล้ว |
| cancel | ยกเลิก |
| delete / remove | ลบ / นำออก |
| edit | แก้ไข |
| create / add / new | สร้าง / เพิ่ม / ใหม่ |
| search | ค้นหา |
| filter | ตัวกรอง (action: กรอง) |
| export / import | ส่งออก / นำเข้า |
| upload / download | อัปโหลด / ดาวน์โหลด |
| apply | นำไปใช้ |
| confirm | ยืนยัน |
| close (dialog) | ปิด |
| loading | กำลังโหลด… |
| error / warning | ข้อผิดพลาด / คำเตือน |
| refresh / retry | รีเฟรช / ลองอีกครั้ง |
| status | สถานะ |
| amount / total | จำนวนเงิน / ยอดรวม |
| date / description / reference | วันที่ / คำอธิบาย / เลขที่อ้างอิง |
| notes | หมายเหตุ |
| permissions / group / user / role | สิทธิ์ / กลุ่ม / ผู้ใช้ / บทบาท |
| admin / superadmin | ผู้ดูแลระบบ / ผู้ดูแลระบบสูงสุด |
| enabled / disabled | เปิดใช้งาน / ปิดใช้งาน |
| active / inactive | ใช้งานอยู่ / ไม่ได้ใช้งาน |
| optional / required | ไม่บังคับ / จำเป็น |
| preview | ดูตัวอย่าง |
| select / selected | เลือก / ที่เลือก |
| file / folder | ไฟล์ / โฟลเดอร์ |
| language / theme | ภาษา / ธีม |
| model | โมเดล |
