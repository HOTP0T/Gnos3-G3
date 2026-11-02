# Gnos3 business modules — Kabyle (Taqbaylit, kab-DZ) glossary

## Conventions

- **Script and spelling**: Latin Kabyle orthography as in the app's existing `kab-DZ/translation.json` and Mozilla's Kabyle localisation: ɛ ɣ ḍ ḥ ṛ ṣ ṭ ẓ č ǧ, tense/doubled consonants written double (Sekles, Ttxil), the hyphen on affixed particles (Snulfu-d, rnu-t, ttxil-k·m), the state of annexation after prepositions (n umiḍan, n yimiḍanen, n tfaturt, n tebzert, n useggas).
- **Form of address**: second person singular, gender-neutral where the verb allows it (tebɣiḍ, tekkseḍ, ad tesnulfuḍ). Where a pronoun suffix shows gender, write both with the middle dot, as the existing catalog does: -ik·im, ttxil-k·m, kečč·mm. Prefer impersonal or passive phrasing for status and error messages ("Ur yessaweḍ ara ad…", "Yettwasekles", "Ulac…").
- **Buttons and menu items**: the bare imperative singular, as in the existing catalog: Sekles, Semmet, Kkes, Ẓreg, Rnu, Snulfu-d, Sentem, Sifeḍ, Kter, Sader, Snes. Object after the verb: "Snulfu-d tira", "Sifeḍ ɣer Excel".
- **Sentence case** for titles, tabs and buttons. ALL-CAPS statement totals in the English stay in capitals.
- **Punctuation**: no space before ":" "?" "!" (as in the existing Kabyle catalog); quoted UI labels and values in « » ( «{{name}}» ); the real ellipsis "…" ("Aɛebbi…"); "amedya:" for "e.g."; the en dash / em dash as in the source.
- **Numbers and dates**: decimal comma and a space (or dot) for thousands as in Algerian French practice (1 234,56 DZD — the app formats numbers itself); dates dd/mm/yyyy; 24-hour clock; month and weekday names come from the app's locale code, never typed into strings.
- **Abbreviations**: DB / KR for debit / credit (DR / CR); TVA for VAT (as used in Algeria); AA for fiscal year (FY = aseggas adrimani); AI stays "AI" (tiḥerci tamegwant, AI). Statement totals in capitals stay in capitals.
- **Placeholders**: `{{name}}` (UI) and `{name}` (server messages) are kept exactly. Kabyle nouns change form after "n" and other prepositions, so never put a placeholder where its state would have to change; write "amiḍan {{code}}", "tafaturt {{number}}", "takebbanit «{{name}}»".
- **Product and data names stay**: Gnos3, K4mi, SmartOffice, Ollama, Open WebUI, Excel, PDF, CSV, JSON, currency codes, MPF, IRD, account codes, HKFRS, PCG, CAS.

## Bookkeeping

| English | Kabyle | Notes |
|---|---|---|
| accounting | tasiḍent | "accountant" = amsiḍen |
| account (ledger) | amiḍan (pl. imiḍanen) | `Account_gnos3`; n umiḍan / n yimiḍanen |
| account name / code | isem n umiḍan / tangalt n umiḍan | |
| chart of accounts | aɣawas n yimiḍanen | |
| sub-account | ddaw-amiḍan (pl. ddaw-imiḍanen) | like ddaw-akaram (subfolder) |
| parent account | amiḍan amaraw | |
| control account | amiḍan n usenqed | an account with sub-accounts |
| journal entry / entry / transaction (ledger) | tira (pl. tirawin) | n tira; "Transaction" in the ledger UI is always an entry |
| entry line / posting | izirig (pl. izirigen) | |
| journal | aɣmis n tsiḍent / aɣmis | |
| general ledger / ledger | adlis ameqqran | n wedlis ameqqran |
| sub-ledger | ddaw-adlis | |
| balance (of an account) | amizan | n umizan |
| opening / closing balance | amizan n ulday / amizan n umdal | |
| trial balance | amizan amatu | |
| balance sheet | abilan | |
| profit and loss / income statement | tagmert d usruḥu | |
| profit / loss | tagmert / asruḥu | n tegmert / n usruḥu |
| net / gross | tazedgant (taɣbalut) / tamatut | "tagmert tazedgant" = net income |
| revenue / income | tinekcamin | n tnekcamin |
| expenses (account type, P&L) | tisuffaɣ (sg. tasuffeɣt) | n tsuffaɣ |
| assets / current / non-current | ayla / ayla n wakud awezzlan / ayla n wakud aɣezfan | |
| liabilities | imrusen | debts |
| equity | idrimen udmawanen | |
| retained earnings | tagmert yettwaḥerzen | |
| debit / credit | adebit / akridi (DB / KR) | |
| draft | arewway (pl. irewwayen) | as in Mozilla's Drafts |
| post / posted | ẓmem / yettwaẓmem, tettwaẓmem (tira) | "Ẓmem tira" |
| void / voided | sefsex / yettwasefsex, tettwasefsex | never "Semmet" (= Cancel) |
| reversal entry | tira tanemgalt | |
| booking (an invoice) | asekcem ɣer tsiḍent / sekcem ɣer tsiḍent | |
| gap (line awaiting an account) | izirig yettraǧun amiḍan | |
| period (accounting) | tallit (n tsiḍent) | close / reopen = mdel / ales-as alday |
| fiscal year / FY | aseggas adrimani / AA | |
| year to date (YTD) | seg tazwara n useggas | |
| year-end closing | amdal n useggas adrimani | |
| closing checklist | asenqed send amdal | |
| template | tamudemt (pl. timudmiwin) | |
| categorization rule | alugen n usmizzwer | |
| split | bḍu / tabḍit | |
| fixed asset | ayla iṣeḥḥan (n wakud aɣezfan) | |
| depreciation | asenqes n wazal | |
| company | takebbanit (pl. tikebbaniyin) | n tkebbanit |
| legal entity name | isem unṣib n tkebbanit | |

## Banking, payments, currencies

| English | Kabyle | Notes |
|---|---|---|
| bank | tabanka | n tbanka |
| bank account | amiḍan n tbanka | |
| bank statement | aɣmis n tbanka | |
| bank line | izirig n tbanka | |
| bank reconciliation | asdukkel n tbanka | |
| match / unmatch / matched | sdukkel / kkes asdukkel / yettusdukkel | |
| match group | agraw n usdukkel | |
| payment | axelleṣ (pl. ixelleṣen) | pay = xelleṣ |
| payment in / out | axelleṣ i d-ikecmen / axelleṣ i yeffɣen | |
| payer / payee | amxelleṣ / amaṭṭaf | |
| payment method | tarrayt n uxelleṣ | |
| bank transfer / check / card / cash | asiweḍ n tbanka / ccik / takarḍa n tbanka / idrimen s ufus | |
| supplier / vendor | asaǧǧaw (pl. isaǧǧawen) | |
| customer | amsaɣ (pl. imsaɣen) | |
| counterparty | tama tayeḍ | |
| accounts payable | imrusen ɣer yisaǧǧawen | |
| accounts receivable | imrusen n yimsaɣen | |
| invoice / bill | tafaturt (pl. tifaturin) | n tfaturt |
| receipt | awṣil (pl. iwṣilen) | |
| amount | azal | n wazal |
| total | asemday | |
| currency | tadrimt (pl. tidrimin) | n tedrimt |
| base currency | tadrimt tagejdant | |
| exchange rate | afmiḍi n usnifel | rate = afmiḍi |
| exchange gain / loss / difference | tagmert n usnifel / asruḥu n usnifel / amgired n usnifel | |

## Taxes

| English | Kabyle | Notes |
|---|---|---|
| tax | tabzert (pl. tibezrin) | n tebzert |
| VAT | TVA | "tabzert ɣef wazal yettwarnan" when spelt out |
| output / input VAT | TVA yettwalqeḍ / TVA ara yettwakksen | |
| GST / sales tax / consumption tax | GST / tabzert ɣef yizenzen / tabzert ɣef useqdec | |
| corporate income tax (CIT) | tabzert ɣef tegmert n tkebbaniyin | |
| profits tax (Hong Kong) | tabzert ɣef tegmert | |
| individual income tax (IIT) | tabzert ɣef tnekcamin n yimdanen | |
| provisional tax | tabzert taseɣlit | |
| tax return / filing | aselɣu n tebzert | |
| assessment notice | tazmilt n tebzert | |
| settlement entry | tira n ufras | |
| tax role mapping | asuddes n tmlilin n tebzert | mapped = yettwasuddes |

## Documents and modules

| English | Kabyle | Notes |
|---|---|---|
| document | isemli (pl. isemliyen) | n yisemli |
| tag | tabzimt (pl. tibzimin) | existing catalog |
| custom field | urti udmawan (pl. urtiyen udmawanen) | |
| correspondent | anermas (pl. inermasen) | |
| document type | anaw n yisemli | |
| workflow | akala n umahil | |
| business card | takarḍa n tnezzut | |
| expense sheet | tiferkit n tsuffaɣ | `Expenses_tab` = tisuffaɣ |
| reimbursement / reimburse | tuɣalin n yidrimen / rr-d idrimen | |
| employee | amaxdam (pl. imaxdamen) | |
| approve / reject / submit | qbel / agi / azen | |
| needs review / reviewed | yeḥwaǧ asenqed / yettwasenqed | |
| report | aneqqis (pl. ineqqisen) | |
| anonymise | ffer isefka udmawanen | Anonymiser stays the module name |

## Interface

| English | Kabyle | Notes |
|---|---|---|
| settings | Iɣewwaren | existing catalog |
| dashboard | Tafelwit n usenqed | |
| save / cancel | Sekles / Semmet | existing catalog |
| delete / remove | Kkes | |
| edit | Ẓreg | |
| add / create | Rnu / Snulfu-d | |
| update | Leqqem | |
| search | Nadi (verb) / Anadi (noun) | |
| filter | Sizdeg (verb) / Imsizdeg (noun) | |
| export / import | Sifeḍ / Kter | nouns: asifeḍ / aktar |
| upload / download | Sali / Sader | nouns: asali / asader |
| apply | Snes | |
| confirm | Sentem | |
| close / open | Mdel / Ldi | |
| loading… | Aɛebbi… | |
| error / warning | Tuccḍa / Ɣur-k·m | |
| name / description / date / status | Isem / Aglam / Azemz / Addad | |
| yes / no | Ih / Uhu | |
| select | Fren | |
| preview | Taskant | |
| file / folder | Afaylu / Akaram | |
| user / group / permissions | Aseqdac / Agraw / Tisirag | |
| language | Tutlayt | |
