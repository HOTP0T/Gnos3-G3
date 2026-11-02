# Gnos3 — Galician (gl-ES) glossary

## Conventions

- **Language standard**: normative Galician (RAG / ILG norms). Never Spanish words or spellings: *xestión*, *xerar*, *engadir*, *ficheiro*, *contrasinal*, *seguinte*, *erro*, *nome*, *data* (date), *moeda*, *imposto*, *pagamento*. The existing Open WebUI gl-ES file mixes in Spanish ("Nombre", "Ninguno", "Agregar", "Error", "Arquivo"); do not copy those.
- **Register**: formal *vostede*, used sparingly. Prefer impersonal or infinitive wording; when addressing the reader use the 3rd person singular ("Seleccione un período", "Revíseo en Asentos", "Quere continuar?", "a súa empresa"). Never *ti* forms ("Selecciona", "o teu").
- **Buttons and menu items**: infinitive, sentence case ("Gardar", "Crear asento", "Marcar como revisada"). Titles and labels: sentence case (only the first word and proper nouns capitalised). Month and weekday names lower case (*xaneiro*, *luns*).
- **Punctuation**: no opening ¿ ¡ (Galician software convention). Quoted UI labels and names go in angular quotes with no inner spaces: «{{name}}», «Obter agora». Literal file column headers the importer expects ('Code', 'Name', 'Line ID') stay in English and in their original quotes. Ellipsis "…". "e.g." → "p. ex.". DR / CR → D / H (debe / haber). Percent with a space in prose is not needed: keep "16,5%" as the source writes it.
- **Numbers and dates**: decimal comma, thousands with a period or a thin space (formatting is done by code; do not change numbers inside strings unless they are prose). Dates written as "31 de marzo", "1 de abril – 31 de marzo".
- **Contractions** are mandatory: do, da, no, na, ao, á, co, coa, polo, pola, dun, dunha, nun, nunha.
- **Gender**: *a conta, o asento, a factura, o pagamento, a empresa, o período, o exercicio, a moeda, o IVE, a declaración, a regra, o modelo, a liña, o extracto, a etiqueta, o documento, a folla de gastos*. Status labels agree with the noun they describe; when the noun is unknown use the masculine (Pagado, Vencido, Aprobado, Rexeitado, Enviado, Aberto, Pechado).
- A `{{tax}}` / `{tax}` placeholder filled with a VAT-type name is treated as masculine ("o {{tax}} repercutido", "do {{tax}}"); income-tax templates put the name first or in parentheses so they also read with "Imposto sobre sociedades".
- Product names unchanged: Gnos3, K4mi, SmartOffice, Ollama, Open WebUI, Excel, PDF, CSV, MPF, currency codes, units.

## UI words

| English | Galician | Notes |
|---|---|---|
| settings | Configuración | as in the app's gl-ES file |
| dashboard | panel | |
| save | gardar | |
| cancel | cancelar | |
| delete | eliminar | |
| remove (from a list) | quitar | |
| edit | editar | |
| add | engadir | never "agregar" |
| create | crear | |
| search | buscar / busca | noun: busca |
| filter | filtrar / filtro | |
| export / import | exportar / importar | |
| upload | subir | |
| download | descargar | |
| apply | aplicar | |
| confirm | confirmar | |
| close (a dialog) | pechar | |
| loading… | cargando… | |
| error | erro | |
| warning | aviso | |
| refresh / reload | actualizar / recargar | |
| file | ficheiro | never "arquivo" (= archive) |
| archive / archived | arquivar / arquivado | |
| name | nome | |
| date | data | |
| amount | importe | |
| status | estado | |
| select / choose | seleccionar / escoller | |
| show / hide | mostrar / ocultar | |
| user / group / role / permissions | usuario / grupo / rol / permisos | |
| sign in / sign out | iniciar sesión / pechar sesión | |
| email | correo electrónico | |
| address (postal) | enderezo | |
| next / previous | seguinte / anterior | |
| yes / no | si / non | |
| needs review / mark reviewed | require revisión / marcar como revisado | "Pending review" = pendente de revisión |
| click (instruction) | premer ("Prema Gardar", "Prema para editar") | never "clic" / "faga clic" |
| tab | lapela | |
| retry / try again | tentar de novo / "Ténteo de novo." | |
| not found (errors) | "Non se atopou o asento" | |
| failed to … | "Erro ao …" / "Non se puido …" | |
| no … yet | "Aínda non hai …" | |
| attach / attachment | achegar / anexo | |
| shortcut | atallo | |
| AI | IA | |
| model (AI) | modelo (de IA) | |
| template | modelo | "modelo de plan de contas", "modelo de períodos" |

## Bookkeeping

| English | Galician | Notes |
|---|---|---|
| account (ledger) | conta | Account_gnos3 |
| account name | nome da conta | |
| chart of accounts | plan de contas | |
| control account (with sub-accounts) | conta de control | |
| sub-account | subconta | |
| parent account | conta nai | |
| detail / leaf account | conta de detalle (de último nivel) | |
| journal entry, entry, transaction (ledger) | asento | |
| posting (entry line) | apuntamento | |
| journal | diario | |
| general ledger, ledger | libro maior | |
| sub-ledger | libro auxiliar | |
| trial balance | balance de sumas e saldos | |
| balance sheet | balance (de situación) | |
| profit and loss / income statement | (conta de) perdas e ganancias | |
| statement of financial position (HK) | estado de situación financeira | |
| statement of profit or loss (HK) | estado de resultados | |
| debit / credit (columns) | debe / haber (D / H) | verbs: cargar / aboar |
| draft | borrador | |
| post / posted | contabilizar / contabilizado | |
| void / voided | anular / anulado | "Void" button = "Anular asento" |
| reversal (entry) | contraasento | |
| book (an invoice) / booking | rexistrar / rexistro (contable) | kept apart from "post" |
| booking engine | motor de rexistro | |
| booking defaults | contas predeterminadas de rexistro | |
| gap (line awaiting an account) | liña pendente | |
| blocker | impedimento | |
| fiscal year, FY | exercicio, Ex. | |
| year to date (YTD) | acumulado do exercicio | |
| accounting period | período contable | |
| close / reopen a period | pechar / reabrir un período | |
| year-end closing | peche do exercicio | |
| closing checklist | comprobacións de peche | |
| retained earnings | resultados de exercicios anteriores | |
| opening / closing balance | saldo de apertura / saldo de peche | |
| assets / liabilities / equity | activo / pasivo / patrimonio neto | |
| current / non-current | corrente / non corrente | |
| revenue / expense(s) (account type) | ingresos / gastos | |
| gross profit / operating profit / net income | marxe bruta / resultado de explotación / resultado neto | |
| fixed asset | inmobilizado | |
| depreciation / accumulated depreciation | amortización / amortización acumulada | |
| book value / salvage value / useful life | valor contable / valor residual / vida útil | |

## Parties, payments, banking

| English | Galician | Notes |
|---|---|---|
| vendor / supplier | provedor | |
| customer / client | cliente | |
| counterparty | contrapartida | |
| accounts payable / receivable | contas a pagar / contas a cobrar | |
| aging | antigüidade de saldos | bucket = tramo; current = non vencido |
| invoice / bill | factura / factura recibida | |
| receipt (expense) | xustificante | |
| payment | pagamento | payment in / out = cobro / pagamento |
| payer / payee | pagador / beneficiario | |
| bank transfer / cheque / card / cash | transferencia bancaria / cheque / tarxeta / efectivo | |
| bank statement | extracto bancario | |
| bank line | movemento bancario | |
| bank reconciliation | conciliación bancaria | |
| match / unmatch / matched / unmatched | conciliar / desfacer a conciliación / conciliado / sen conciliar | |
| match group | grupo de conciliación | |
| bank fee | comisión bancaria | |
| currency / base currency / foreign currency | moeda / moeda base / moeda estranxeira | |
| exchange rate | tipo de cambio | "rate" alone = tipo |
| exchange gain / loss | diferenzas positivas / negativas de cambio | |
| exchange clearing account | conta ponte de cambio | |
| rate override (per company) | tipo propio | |
| categorization rule | regra de categorización | bank-line rule = regra de movementos bancarios |
| pattern | patrón | |
| split (across accounts) | repartir / repartición | |
| company | empresa | |
| legal name | razón social | |

## Tax

| English | Galician | Notes |
|---|---|---|
| tax | imposto | |
| VAT | IVE | imposto sobre o valor engadido |
| output / input VAT | IVE repercutido / IVE soportado | |
| VAT payable / VAT credit | IVE a ingresar / IVE a compensar | generic "{{tax}} payable" = "{{tax}} a pagar" |
| GST / sales tax / consumption tax | GST / imposto sobre as vendas / imposto sobre o consumo | |
| surcharge (China) | recargo | |
| corporate income tax (CIT) | imposto sobre sociedades | |
| individual income tax (IIT) | imposto sobre a renda das persoas físicas (IRPF) | |
| profits tax (Hong Kong) | imposto sobre os beneficios | |
| provisional tax / instalment | pagamento á conta / prazo | |
| assessment notice / demand note | notificación de liquidación / notificación de pagamento | |
| tax return, filing | declaración | filed = presentada |
| accrual (entry) | (asento de) devindicación | |
| settlement / settle | liquidación / liquidar | |
| assessable profit | base impoñible | |
| add-back / deduction | aumento / diminución | tax-computation adjustments = axustes fiscais |
| losses brought forward | bases impoñibles negativas de exercicios anteriores | |
| withholding | retención | |
| tax role / map / mapped | función fiscal / asignar / asignada | |
| tax office | administración tributaria | |

## Expenses, documents, other modules

| English | Galician | Notes |
|---|---|---|
| expense sheet | folla de gastos | Expenses_tab (the employee-expenses tab) = Gastos |
| trip (expense app) | viaxe | |
| reimbursement | reembolso | |
| employee / approver | empregado / aprobador | |
| approve / reject / submit | aprobar / rexeitar / enviar | |
| merchant | comercio | |
| business card | tarxeta de visita | |
| job title | cargo | |
| document | documento | |
| tag | etiqueta | K4mi tag = etiqueta de K4mi |
| custom field | campo personalizado | |
| correspondent | interlocutor | |
| document type | tipo de documento | |
| storage path | ruta de almacenamento | |
| workflow | fluxo de traballo | |
| knowledge base | base de coñecemento | |
| anonymise / anonymiser | anonimizar / Anonimizador | |
| encrypt / decrypt | cifrar / descifrar | |
| sync | sincronizar / sincronización | |
