# zh-CN glossary (Simplified Chinese, PRC practice)

Term choices used across `zh-CN.ui.json` and `zh-CN.books.json`.

## Ledger and entries

| English | 中文 | Note |
|---|---|---|
| Account (ledger) | 科目 | never 账户/账号 for a ledger account |
| Chart of accounts | 科目表 | |
| Account code / name | 科目编码 / 科目名称 | |
| Sub-account, detail account, leaf account | 明细科目（末级科目） | |
| Control account (has sub-accounts) | 控制科目 | "an account with sub-accounts" = 有下级科目的科目 |
| Parent account / top-level | 上级科目 / 一级科目 | |
| Journal entry, entry, transaction (accounting) | 凭证 | "Journal entries" / "Entries" tab = 凭证 |
| Entry line | 分录 | "Journal lines" = 分录 |
| Description (entry) | 摘要 | |
| Reference | 参考号 | |
| Post / posted / unposted | 过账 / 已过账 / 未过账 | |
| Book (an invoice), booking engine | 记账 / 记账引擎 | booking ≠ posting |
| Booking defaults | 记账默认科目 | |
| Draft | 草稿 | |
| Void / voided | 作废 / 已作废 | |
| Reversal (entry) | 冲销凭证 | |
| Gap (line awaiting an account) | 待补项 | |
| Map / mapped | 映射 / 已映射 | |
| Role (account role for a tax) | 用途 | |
| Rule / categorization rules | 规则 / 归类规则 | |
| Counterparty account | 往来科目 | |
| Debit / credit (DR / CR) | 借方 / 贷方（借 / 贷） | |
| General ledger | 总账 | |
| Ledger (books) | 账簿 | |
| Books language | 账簿语言 | |
| Opening balance / closing balance | 期初余额 / 期末余额 | |
| Movement (period) | 本期发生额 | |
| Year to date | 本年累计 | |
| Running balance | 累计余额 | |
| Recurring entries | 定期凭证 | |

## Periods and closing

| English | 中文 | Note |
|---|---|---|
| Accounting period | 会计期间 | |
| Fiscal year / FY | 会计年度 | |
| Calendar year | 自然年度 | |
| Close a period / closed | 结账 / 已结账 | period status "Open" = 未结账 |
| Reopen a period | 反结账 | |
| Year-end closing (entry) | 年末结账（凭证） | |
| Carry-forward entry (result → retained earnings) | 利润结转凭证 | |
| Retained earnings | 未分配利润 | |
| Pre-closing checklist / blocker | 结账前检查清单 / 阻止结账（的问题） | |

## Statements and reports

| English | 中文 | Note |
|---|---|---|
| Trial balance | 试算平衡表 | |
| Profit & loss / Income statement | 利润表 | |
| Balance sheet | 资产负债表 | |
| Cash flow (statement) | 现金流量表 | |
| Statement of financial position / of profit or loss (HK) | 财务状况表 / 损益表 | |
| Statutory statements | 法定财务报表 | |
| Line (statement row number) | 行次 | |
| Note (statement) | 附注 | |
| PRC Small Business Accounting Standard | 小企业会计准则 | CAS lines use the official label_zh verbatim |
| Hong Kong SME-FRS | 香港中小型实体财务报告准则 | |
| Aging / bucket / current | 账龄 / 账龄区间 / 未逾期 | |
| Accounts receivable / payable | 应收账款 / 应付账款 | |
| Revenue / expenses | 收入 / 费用 | |
| Gross / net (asset columns) | 原值 / 净值 | |

## Banking, payments, FX

| English | 中文 | Note |
|---|---|---|
| Bank account | 银行账户 | |
| Bank statement / statement line | 银行对账单 / 银行流水 | |
| Reconcile / reconciliation | 对账 / 银行对账 | |
| Match / unmatch / match group | 匹配 / 取消匹配 / 匹配组 | |
| Payment (generic, in or out) | 收付款 | in = 收款, out = 付款 |
| Record a payment | 登记收付款 | |
| Payer / payee | 付款方 / 收款方 | |
| Exchange rate | 汇率 | |
| Base / company currency | 本位币 / 公司本位币 | |
| Exchange gain / loss / differences | 汇兑收益 / 汇兑损失 / 汇兑差额 | gain/loss account pair = 汇兑损益科目 |
| Exchange clearing account | 汇兑清算科目 | |

## Tax

| English | 中文 | Note |
|---|---|---|
| VAT | 增值税 | |
| Output / input VAT | 销项税额 / 进项税额 | "Output {{tax}}" = {{tax}}销项税额 |
| VAT payable | 应交增值税 | "{{tax}} payable" = 应交{{tax}} |
| VAT credit carried forward | 留抵税额 / 增值税留抵税额 | |
| Surcharges | 附加税费 | 城市维护建设税、教育费附加、地方教育附加 |
| Taxes and surcharges (expense) | 税金及附加 | surcharge "expense" roles = …（税金及附加） |
| Corporate income tax | 企业所得税 | |
| Individual income tax | 个人所得税 | |
| Profits Tax (HK) | 利得税 | two-tier = 两级制 |
| Provisional tax (HK) | 暂缴税 | prepaid income tax = 预缴所得税 |
| Salaries Tax (HK) | 薪俸税 | |
| MPF | 强积金 | |
| GST / GST-HST | 商品及服务税 / 商品及服务税/统一销售税 | |
| Sales tax / consumption tax | 销售税 / 消费税 | |
| Tax return / filing | 申报 / 申报记录 | |
| Tax declaration | 纳税申报 | |
| Accrual (entry) | 计提（凭证） | |
| Settlement entry (VAT) | 结转凭证 | |
| Settle (CIT / profits tax filing) | 清缴 | |
| Add-back / deduction | 调增 / 调减（纳税调增 / 纳税调减） | |
| Assessable profit | 应纳税所得额 | |
| Losses brought forward | 以前年度亏损 | |
| Assessment notice / demand note | 评税通知书 / 缴税通知书 | |

## Other modules

| English | 中文 | Note |
|---|---|---|
| Fixed asset / depreciation / accumulated depreciation | 固定资产 / 折旧 / 累计折旧 | |
| Asset register | 资产台账 | |
| Useful life / salvage value / book value | 使用期限 / 残值 / 账面价值 | |
| Straight-line / declining balance | 直线法 / 余额递减法 | |
| Expense sheet / reimbursement | 报销单 / 报销 | |
| Expense receipt | 票据 | |
| Expense portal | 报销门户 | |
| Employee | 员工 | |
| Approve / approved / pending review | 批准 / 已批准 / 待审核 | |
| Invoice / bill (purchase) | 发票 / 采购发票 | books: Sale = 销售, Bill = 采购 |
| Customer, client / vendor | 客户 / 供应商 | |
| Needs review (extraction) | 需复核 | |
| Confidence | 置信度 | |
| Business card | 名片 | |
| Data source / connector | 数据源 / 连接器 | |
| Superadmin | 超级管理员 | |
| Country (config) | 国家/地区 | Hong Kong is a region |
