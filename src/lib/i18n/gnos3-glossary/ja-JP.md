# Gnos3 — Japanese (ja-JP) glossary

Conventions:

- **Register**: です・ます調 for every sentence (messages, hints, errors, confirmations). No explicit "you" (あなた); address the reader implicitly. Polite requests: 「〜してください」. Errors: 「〜できません」「〜が見つかりません」.
- **Buttons and menu items**: short noun phrases or plain verb nouns, no です・ます: 保存, キャンセル, 仕訳を作成, 転記, 照合を解除. Column headers and labels: nouns (金額, 日付, 摘要).
- **Punctuation**: 、。 (never , . inside Japanese text); full-width （） ： ？ ！; 「」 for quoted UI labels and names (『』 inside 「」); 例： for "e.g."; 〜 for ranges in prose ("1〜12月"), "–" kept in numeric ranges copied from data. "…" for ellipsis. No space between Japanese and numbers, placeholders or Latin words, except where a Latin word would otherwise touch another Latin word.
- **Numbers and dates**: half-width digits; thousands separator ","; dates YYYY/MM/DD in compact places, YYYY年M月D日 in prose; months 1月…12月; percentages "16.5%". Currency codes (JPY, HKD, EUR…) and units stay as they are.
- **Plurals**: Japanese has none: singular and plural source strings get the same text (件, 行, 社 as counters: 「{{count}}件の仕訳」「{{count}}行」).
- **Debit / credit**: 借方 / 貸方; abbreviations DR / CR → 借 / 貸.
- **Taxes**: named from the tax kind: VAT → 付加価値税（VAT）or simply VAT in tight labels; Japanese consumption tax → 消費税; GST → GST; sales tax → 売上税. A `{{tax}}` placeholder is placed so the phrase reads for any of these ("仮受{{tax}}", "{{tax}}申告").
- **Product names** stay: Gnos3, K4mi, SmartOffice, Ollama, Open WebUI, Excel, PDF, CSV, MPF, IRD.

| English | Japanese |
|---|---|
| account (ledger) | 勘定科目（short: 科目） |
| account (user) | アカウント |
| account name / code | 科目名 / 科目コード |
| chart of accounts | 勘定科目表 |
| control account (with sub-accounts) | 統制勘定 |
| sub-account | 補助科目 |
| leaf / detail account | 末端科目 |
| parent account | 親科目 |
| account type: asset / liability / equity / revenue / expense | 資産 / 負債 / 純資産 / 収益 / 費用 |
| journal entry / entry / transaction (booked) | 仕訳 |
| journal | 仕訳帳 |
| line (of an entry) | 明細行（short: 行） |
| ledger / the books | 帳簿 |
| general ledger | 総勘定元帳 |
| sub-ledger | 補助元帳 |
| trial balance | 試算表 |
| balance sheet | 貸借対照表 |
| profit and loss / income statement / P&L | 損益計算書 |
| statement of financial position (HK) | 財政状態計算書 |
| statement of profit or loss (HK) | 純損益計算書 |
| current / non-current assets | 流動資産 / 非流動資産 |
| current / non-current liabilities | 流動負債 / 非流動負債 |
| equity | 純資産 |
| retained earnings | 繰越利益剰余金 |
| net income / profit for the year | 当期純利益 |
| gross profit / operating profit | 売上総利益 / 営業利益 |
| revenue / cost of sales | 売上高 / 売上原価 |
| fiscal year / FY | 会計年度 / 年度 |
| accounting period / period | 会計期間 / 期間 |
| year to date (YTD) | 期首からの累計（short: 累計） |
| opening balance | 期首残高（for a period: 開始残高） |
| closing balance | 期末残高 |
| balance | 残高 |
| debit / credit | 借方 / 貸方 |
| draft | 下書き |
| post / posted | 転記 / 転記済み |
| void / voided | 取消 / 取消済み（button: 仕訳を取消） |
| reversal entry | 逆仕訳 |
| close / reopen a period | 締める / 再開する（期間の締め） |
| year-end closing | 決算（年度末決算） |
| closing checklist | 決算チェックリスト |
| blocker | 阻害要因（「転記できない理由」） |
| gap (line awaiting an account) | 科目未設定の行 |
| book (an invoice) / booking | 計上する / 計上 |
| booking defaults | 既定の計上科目 |
| categorization rule | 分類ルール |
| bank-line rule | 銀行明細ルール |
| pattern | パターン |
| split (across accounts) | 按分 |
| description (of an entry) | 摘要 |
| reference | 参照番号 |
| amount | 金額 |
| company | 会社 |
| legal entity name | 正式名称（法人名） |
| currency / base currency | 通貨 / 基準通貨 |
| exchange rate | 為替レート |
| company rate override | 会社別レート |
| exchange difference / gain / loss | 為替差額 / 為替差益 / 為替差損 |
| exchange clearing account | 為替仮勘定 |
| VAT | 付加価値税（VAT） |
| consumption tax (Japan) | 消費税 |
| output / input VAT | 仮受{{tax}} / 仮払{{tax}} |
| VAT payable / VAT credit carried forward | 未払{{tax}} / 繰越控除額 |
| surcharge (China, on VAT) | 付加税 |
| corporate income tax (CIT) | 法人税 |
| profits tax (Hong Kong) | 利得税 |
| individual income tax (IIT) | 個人所得税 |
| provisional tax | 暫定税（予定納税） |
| prepaid tax (asset) | 前払税金 |
| tax return / filing | 申告 / 申告書 |
| assessment notice / demand note | 課税通知書 / 納付通知書 |
| accrual entry | 計上仕訳 |
| settlement entry | 精算仕訳 |
| settle (a filing) | 精算する |
| tax adjustments / add-back / deduction | 税務調整 / 加算 / 減算 |
| assessable profit | 課税所得 |
| losses brought forward | 繰越欠損金 |
| two-tier / tiered rates | 2段階税率 / 段階税率 |
| tax role mapping / mapped | 科目の割り当て / 割り当て済み |
| invoice | 請求書 |
| bill (supplier invoice) | 仕入請求書 |
| receipt | 領収書 |
| payment / payments (in and out) | 支払 / 入出金 |
| payment in / out | 入金 / 出金 |
| payer / payee | 支払人 / 支払先 |
| payment method | 支払方法 |
| bank transfer / check / credit card / cash | 銀行振込 / 小切手 / クレジットカード / 現金 |
| bank account | 銀行口座 |
| bank statement | 銀行明細 |
| bank line | 銀行明細行 |
| bank reconciliation | 銀行照合 |
| match / matched / unmatch | 照合する / 照合済み / 照合を解除 |
| match group | 照合グループ |
| auto-match | 自動照合 |
| counterparty | 取引先（account: 相手勘定） |
| supplier / vendor | 仕入先 |
| customer / client | 得意先 |
| accounts payable / receivable | 買掛金 / 売掛金 |
| AP / AR aging | 買掛金年齢表 / 売掛金年齢表 |
| fixed asset | 固定資産 |
| depreciation / accumulated depreciation | 減価償却 / 減価償却累計額 |
| useful life / salvage value / book value | 耐用年数 / 残存価額 / 帳簿価額 |
| straight-line / declining | 定額法 / 定率法 |
| expense (account type, P&L) | 費用 |
| expense (an employee's claim) / expenses tab | 経費 / 経費精算 |
| expense sheet | 経費精算書 |
| reimbursement | 立替精算（払い戻し） |
| employee | 従業員 |
| submit / approve / reject | 申請 / 承認 / 却下 |
| template | テンプレート |
| business card | 名刺 |
| needs review / mark reviewed | 要確認 / 確認済みにする |
| document | ドキュメント |
| tag | タグ |
| custom field | カスタムフィールド |
| correspondent | 発信元 |
| document type | ドキュメントタイプ |
| storage path | フォルダー |
| workflow | ワークフロー |
| notes | メモ |
| owner | 所有者 |
| upload / download | アップロード / ダウンロード |
| import / export | インポート / エクスポート |
| settings | 設定 |
| dashboard | ダッシュボード |
| save / cancel / delete / edit | 保存 / キャンセル / 削除 / 編集 |
| search / filter | 検索 / フィルター |
| apply / confirm / discard | 適用 / 確認 / 破棄 |
| reprocess | 再処理 |
| loading… | 読み込み中… |
| error / warning | エラー / 警告 |
| permissions / group | 権限 / グループ |
| superadmin / admin | スーパー管理者 / 管理者 |
| anonymise / anonymiser | 匿名化 / 匿名化ツール（page name: Anonymiser） |
| trip (a group of expenses in the expense app) | 出張 |
| recall (a submitted trip) / resubmit | 取り戻す / 再申請 |
| merchant | 加盟店 |
| portal login | ポータルのログイン |
| Finances (embedded app, sidebar label) | 財務 |
| status: open period / closed period | 未締め / 締め済み |
| aging bucket / "Current" bucket | 期間区分 / 期日未到来 |
