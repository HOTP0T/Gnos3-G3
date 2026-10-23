# zh-TW glossary (Traditional Chinese, Hong Kong-leaning)

Traditional characters throughout. Where Hong Kong and Taiwan accounting terms differ, the Hong Kong term is used. Generic UI words follow the app's existing zh-TW locale (儲存, 建立, 匯入, 匯出, 搜尋, 設定, 載入, 範本). 帳 is used rather than 賬, except in the official HK statement lines, which are shown verbatim from `label_zh`.

## Ledger and entries

| English | 繁體中文 | Note |
|---|---|---|
| Account (ledger) | 科目 / 會計科目 | Never 帳號. `Account_gnos3` → 科目 |
| Chart of accounts | 會計科目表 | Template: 科目表範本 |
| Sub-account / detail (leaf) account | 明細科目 | "leaf" → 末級 |
| Parent account | 上級科目 | |
| Control account | 統制帳戶 | |
| Journal entry / entry / transaction | 分錄 | "Transaction" in the accounting screens means a journal entry, so it is 分錄 too. Entry type "Journal" → 日記帳分錄 |
| Journal lines / line | 分錄行 / 行 | `Line_gnos3` (statement line no.) → 行次 |
| Description (entry) | 摘要 | Bank-line or invoice description → 描述 |
| Reference | 參考編號 | |
| Post / posted / unposted | 過帳 / 已過帳 / 未過帳 | |
| Draft | 草稿 | |
| Void / voided | 作廢 / 已作廢 | |
| Reversal (entry) | 沖銷分錄 | |
| Debit / credit (DR / CR) | 借方 / 貸方 (借 / 貸) | |
| Balanced / unbalanced | 已平衡 / 借貸不平衡 | |
| Booking / book (an invoice) | 入帳 | Booking defaults → 入帳預設科目 |
| Gap (unresolved line) | 缺口 | |
| Counterparty account | 對方科目 | |
| Rule / categorization rule | 規則 / 分類規則 | Bank line rule → 銀行明細規則 |
| Role (tax role of an account) | 用途 | `Role_gnos3`. Tax roles → 稅務用途 |
| Mapped / not mapped | 已對應 / 未對應 | |

## Periods and closing

| English | 繁體中文 | Note |
|---|---|---|
| Accounting period | 會計期間 | |
| Fiscal year | 財政年度 | FY → 財政年度 |
| Year end | 年結日 | Year-end closing → 年結 |
| Close period / closed | 結帳 / 已結帳 | Status "Open" → 未結 |
| Opening balance | 期初結餘 | |
| Closing / ending balance | 期末結餘 | |
| Brought forward | 承前 | Balance brought forward → 承前結餘 |
| Carry forward | 結轉 | |
| Retained earnings | 保留溢利 | |
| Year to date | 本年累計 | Lowercase fragment → 本年至今 |
| Movement (TB) | 本期發生額 | |
| Blocker (closing check) | 阻止項 | |

## Statements and reports

| English | 繁體中文 | Note |
|---|---|---|
| General ledger | 總分類帳 | GL account → 總帳科目 |
| Trial balance | 試算表 | |
| Profit & loss / income statement / statement of profit or loss | 損益表 | |
| Balance sheet | 資產負債表 | |
| Statement of financial position (SoFP) | 財務狀況表 | |
| Cash flow (statement) | 現金流量表 | Operating / investing / financing → 經營 / 投資 / 融資 |
| Revenue | 收益 | As in the HK SME-FRS statement. "Income" (French headings) → 收入 |
| Expense(s) | 費用 | Tax-computation presets → 開支 |
| Gross profit / operating profit / net income | 毛利 / 經營溢利 / 淨溢利 | |
| Assets / liabilities / equity | 資產 / 負債 / 權益 | Owner's equity → 擁有人權益 |
| Statutory statements | 法定財務報表 | |
| Hong Kong SME-FRS | 香港中小型實體財務報告準則 | |
| PRC Small Business Accounting Standard | 中國小企業會計準則 | |
| Note (statement note) | 附註 | `Note_gnos3`. `Notes_gnos3` → 備註 |

## Receivables, payables, bank

| English | 繁體中文 | Note |
|---|---|---|
| Accounts receivable / payable | 應收帳款 / 應付帳款 | |
| Aging / age bucket | 帳齡 / 帳齡區間 | "Current" bucket → 未到期 |
| Customer / client | 客戶 | |
| Vendor / supplier | 供應商 | |
| Invoice / bill | 發票 / 帳單 | |
| Payment(s) | 收付款 | Payment in / out → 收款 / 付款 |
| Bank reconciliation / reconcile | 銀行對帳 / 對帳 | |
| Bank statement / bank line | 銀行對帳單 / 銀行明細 | |
| Match / unmatched / match group | 配對 / 未配對 / 配對組 | Rule matching → 比對 |
| Cheque (payment method "Check") | 支票 | |

## Fixed assets, expenses

| English | 繁體中文 | Note |
|---|---|---|
| Fixed asset / asset register | 固定資產 / 資產登記冊 | |
| Depreciation / accumulated depreciation | 折舊 / 累計折舊 | |
| Straight-line / declining balance | 直線法 / 遞減餘額法 | |
| Useful life / salvage value / book value | 可使用年期 / 殘值 / 帳面值 | |
| Expense sheet / reimbursement | 報銷單 / 報銷 | |
| Receipt (expense) | 收據 | |
| Employee / approver | 員工 / 核准人 | Approve → 核准; reject → 退回 |
| Business card | 名片 | |

## Tax

| English | 繁體中文 | Note |
|---|---|---|
| VAT / GST / GST/HST | 增值稅 / 商品及服務稅 / 商品及服務稅／統一銷售稅 | |
| Sales tax / consumption tax / ICMS | 銷售稅 / 消費稅 / ICMS | |
| Output / input tax | 銷項稅額 / 進項稅額 | "Output {{tax}}" → {{tax}}銷項稅額 |
| {{tax}} payable | 應付{{tax}} | |
| Credit brought / carried forward (VAT) | 上期結轉留抵稅額 / 結轉留抵稅額 | |
| Surcharges | 附加稅費 | 城市維護建設稅, 教育費附加, 地方教育附加 |
| Corporate income tax | 企業所得稅 | |
| Profits Tax (HK) | 利得稅 | Two-tiered rates → 兩級制稅率 |
| Provisional tax | 暫繳稅 | Demand note → 繳稅通知書 |
| Assessable profit / adjusted profit | 應評稅利潤 / 經調整利潤 | |
| Tax computation / worksheet | 稅務計算表 / 計算表 | |
| Add-back / deduction | 加回項目 / 扣減項目 | |
| Losses brought forward | 承前虧損 | |
| Tax reduction (one-off rebate) | 稅款寬減 | |
| Assessment notice / year of assessment | 評稅通知書 / 課稅年度 | |
| Accrual entry / settlement entry | 應計分錄 / 結算分錄 | Accrued → 已計提 |
| Over- / under-provision | 超額撥備 / 撥備不足 | Provisions → 撥備 |
| Individual income tax | 個人所得稅 | Salaries Tax (HK) → 薪俸稅 |
| MPF | 強積金 | Contributions → 供款; trustee → 受託人 |
| Filing / filings | 申報 / 申報記錄 | |
| Tax authority | 稅務機關 | |

## Currency

| English | 繁體中文 | Note |
|---|---|---|
| Exchange rate | 匯率 | Rate on file → 已存匯率; live rates → 即時匯率 |
| Exchange gain / loss | 匯兌收益 / 匯兌虧損 | |
| Exchange clearing account | 匯兌清算帳戶 | |
| Base currency | 本位幣 | |
| From / to currency | 原幣 / 目標貨幣 | |
