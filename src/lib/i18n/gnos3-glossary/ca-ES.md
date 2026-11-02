# Gnos3 business modules — Catalan (ca-ES) glossary

## Conventions

- **Form of address: "vós"** (the polite register of Catalan software: Mozilla, LibreOffice, Softcatalà style), with the adjective in the singular: "Esteu segur que voleu eliminar…?", "Seleccioneu un període", "Reviseu-ho a Assentaments". Prefer impersonal phrasing when it reads naturally ("No s'ha pogut desar…"). Never "tu" in the business modules (Open WebUI's own chat screens use "tu"; leave them as they are).
- **Buttons and menu items: infinitive**, as in the app's existing ca-ES file: "Desar", "Cancel·lar", "Eliminar", "Crear l'assentament", "Exportar a Excel".
- **Sentence case** for titles, tabs and buttons ("Balanç de sumes i saldos", not "Balanç De Sumes…").
- **Punctuation**: no space before ":" "?" "!"; Catalan quotes « » for quoted labels and values («{{name}}»); real ellipsis "…" ("Carregant…"); "p. ex." for "e.g."; the middle dot is part of the word (cancel·lar, anul·lar, col·laborador).
- **Apostrophes and placeholders**: do not elide in front of a placeholder whose first letter is unknown; rephrase or quote it: "de «{{name}}»", "el compte {{code}}", "la factura {{number}}". Avoid an article in front of a tax-name placeholder ({{tax}} / {tax} can be IVA = l'IVA, or another tax): write "{{tax}} repercutit", "{{tax}} a ingressar", "declaració de {{tax}}" is acceptable only when the noun before it carries the meaning.
- **Numbers and dates**: decimal comma, thousands with a dot (1.234,56 €; the app formats numbers itself); dates dd/mm/aaaa; the 24-hour clock; months and weekdays in lower case (gener, dilluns).
- **Abbreviations**: D / H for debit / credit (DR / CR); Ex. for fiscal year (FY); PiG for P&L; IA for AI; NIF for tax ID. Statement totals written in capitals in English stay in capitals.
- **Product and data names stay**: Gnos3, K4mi, SmartOffice, Ollama, Open WebUI, Excel, PDF, CSV, currency codes, MPF, IRD, account codes.

## Bookkeeping

| English | Catalan | Notes |
|---|---|---|
| account (ledger) | compte | `Account_gnos3` |
| account name | nom del compte | |
| chart of accounts | pla de comptes | |
| sub-account / detail (leaf) account | subcompte / compte de detall (darrer nivell) | |
| control account | compte de control | an account with sub-accounts |
| parent account | compte pare | |
| journal entry / entry / transaction (journal) | assentament | "Transaction" in the ledger UI is always an entry |
| posting (entry line) | apunt | |
| line | línia | |
| journal | llibre diari / diari | |
| general ledger / ledger | llibre major | |
| sub-ledger | llibre auxiliar | |
| trial balance | balanç de sumes i saldos | |
| balance sheet | balanç | |
| profit & loss / income statement | compte de pèrdues i guanys (PiG) | |
| statement of financial position (HK) | estat de situació financera | |
| statement of profit or loss (HK) | estat de resultats | |
| statutory statements | comptes anuals | |
| debit / credit | deure / haver (D / H) | verbs: carregar / abonar |
| debit / credit balance | saldo deutor / saldo creditor | |
| draft | esborrany | |
| post / posted | comptabilitzar / comptabilitzat | |
| void / voided | anul·lar / anul·lat | button: "Anul·lar l'assentament" |
| reversal (entry) | contraassentament | |
| book (an invoice) / booking | registrar / registre (comptable) | kept apart from "post" |
| booking engine | motor de registre | |
| booking defaults | comptes predeterminats de registre | |
| gap (line awaiting an account) | línia pendent | |
| fiscal year / FY | exercici / Ex. | |
| year to date (YTD) | acumulat de l'exercici | |
| accounting period | període comptable | |
| close / reopen a period | tancar / reobrir un període | |
| year-end closing | tancament de l'exercici | |
| closing checklist | comprovacions de tancament | |
| blocker | punt bloquejant | |
| carry-forward entry | assentament de traspàs del resultat | |
| retained earnings | resultats d'exercicis anteriors | statement line: resultats no distribuïts |
| opening / closing balance | saldo d'obertura / saldo de tancament | |
| assets / liabilities / equity | actiu / passiu / patrimoni net | |
| current / non-current | corrent / no corrent | |
| revenue / income | ingressos | |
| expenses (account type, P&L) | despeses | |
| gross profit / operating profit / net income | marge brut / resultat d'explotació / resultat net | |
| fixed asset | immobilitzat | material / intangible / financer |
| depreciation / accumulated depreciation | amortització / amortització acumulada | |
| book value / salvage value / useful life | valor comptable / valor residual / vida útil | |
| linear / declining (method) | lineal / decreixent | |
| asset register | registre d'immobilitzat | |
| template | plantilla | chart / period template = plantilla de pla de comptes / de períodes |

## Parties, payments, banking

| English | Catalan | Notes |
|---|---|---|
| company | empresa | |
| legal entity name | raó social | |
| vendor / supplier | proveïdor | |
| client / customer | client | |
| counterparty | contrapartida | |
| accounts payable / receivable (AP / AR) | comptes a pagar / comptes a cobrar | |
| aging, bucket, current (not yet due) | antiguitat de saldos, tram, no vençut | |
| invoice / bill (supplier invoice) | factura / factura rebuda | |
| receipt (expense proof) | justificant | a cash receipt = rebut |
| payment / payment in / payment out | pagament / cobrament / pagament | |
| payer / payee | pagador / beneficiari | |
| payment method | mètode de pagament | |
| bank transfer / check / credit card / cash | transferència bancària / xec / targeta de crèdit / efectiu | |
| bank statement | extracte bancari | |
| bank line / bank statement line | moviment bancari | |
| bank reconciliation | conciliació bancària | |
| match / unmatch / matched / unmatched | conciliar / desfer la conciliació / conciliat / sense conciliar | |
| match group | grup de conciliació | |
| bank fee | comissió bancària | |
| currency / base currency / foreign currency | moneda / moneda base / moneda estrangera | |
| exchange rate | tipus de canvi | "Rate" alone = tipus |
| exchange gain / loss | diferències positives / negatives de canvi | |
| exchange clearing account | compte pont de canvi | |
| rate override (per company) | tipus propi | |
| categorization rule | regla de categorització | bank-line rule = regla de moviments bancaris |
| pattern | patró | |
| split (across accounts) | desglossar / desglossament | |

## Tax

| English | Catalan | Notes |
|---|---|---|
| VAT | IVA | masculine; avoid the article before `{{tax}}` |
| GST / GST-HST / sales tax / consumption tax | GST / GST-HST / impost sobre les vendes / impost sobre el consum | |
| output / input VAT | IVA repercutit / IVA suportat | |
| VAT payable / VAT credit | IVA a ingressar / IVA a compensar | generic `{{tax}} payable` = "{{tax}} a pagar" |
| credit brought / carried forward | crèdit de períodes anteriors / crèdit a compensar | |
| surcharge (China) | recàrrec | urban construction / education / local education |
| corporate income tax (CIT) | impost sobre societats (IS) | |
| individual income tax (IIT) | impost sobre la renda de les persones físiques (IRPF) | |
| profits tax (Hong Kong) | impost sobre els beneficis | |
| provisional (prepaid) tax / instalment | pagament a compte / termini | |
| assessment notice / demand note | notificació de liquidació / notificació de pagament | |
| tax return / filing | declaració | filed = presentada |
| accrual (entry) | (assentament de) meritació | |
| settlement / settle | liquidació / liquidar | |
| add-back / deduction (tax computation) | augment / disminució | |
| assessable profit | base imposable | |
| losses brought forward | bases imposables negatives d'exercicis anteriors | |
| two-tier / tiered rates | tipus en dos trams / tipus per trams | |
| tax role / map / mapped | funció fiscal / assignar / assignat | |
| tax authority | administració tributària | |
| withholding | retenció | |

## Expenses, documents, other modules

| English | Catalan | Notes |
|---|---|---|
| expense sheet | nota de despeses | `Expenses_tab` = Notes de despeses |
| expense / reimbursement | despesa / reemborsament | |
| employee / approver | empleat / aprovador | |
| approve / reject / submit | aprovar / rebutjar / enviar | |
| merchant | establiment | |
| business card | targeta de visita | |
| job title | càrrec | |
| needs review / mark reviewed | cal revisar / marcar com a revisat | |
| extraction / reprocess | extracció / tornar a processar | |
| confidence | confiança | |
| anonymise / anonymiser | anonimitzar / Anonimitzador | |
| document | document | |
| tag | etiqueta | as in K4mi |
| custom field | camp personalitzat | as in K4mi |
| correspondent | corresponsal | as in K4mi |
| document type | tipus de document | as in K4mi |
| workflow | flux de treball | |
| knowledge base | base de coneixement | as in Open WebUI |
| group / role / permission | grup / rol / permís | |

## Interface words (from the app's existing ca-ES file)

| English | Catalan |
|---|---|
| settings | Preferències |
| dashboard | tauler |
| save / cancel / delete / remove | Desar / Cancel·lar / Eliminar / Treure (from a list) |
| edit / create / add | Editar / Crear / Afegir |
| search / filter / sort by | Cercar / Filtrar (noun: filtre) / Ordenar per |
| export / import | Exportar / Importar |
| upload / download | Pujar / Descarregar |
| apply / confirm / close / back | Aplicar / Confirmar / Tancar / Enrere |
| loading / saving | Carregant… / Desant… |
| error / warning | error / avís |
| retry / refresh / reset / clear | Tornar-ho a provar / Actualitzar / Restablir / Netejar |
| status / date / amount / total | estat / data / import / total |
| open / view / details | Obrir / Veure / Detalls |
| enabled / disabled | activat / desactivat |
| required / optional | obligatori / opcional |
