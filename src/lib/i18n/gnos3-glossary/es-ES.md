# Gnos3 business modules — Spanish (es-ES) glossary

Register: "usted"-neutral. Buttons and menu items use the infinitive ("Guardar", "Crear asiento"); instructions use the usted imperative ("Seleccione un periodo", "Revíselo en Asientos"). Sentence case. Generic UI vocabulary follows the app's existing es-ES file (Ajustes, Guardar, Cancelar, Limpiar…); "Delete" is "Eliminar" throughout the business modules.

## Bookkeeping

| English | Spanish | Notes |
|---|---|---|
| account | cuenta | |
| chart of accounts | plan de cuentas | |
| sub-account / detail (leaf) account | subcuenta / cuenta de detalle (de último nivel) | |
| control account | cuenta de control | an account with sub-accounts |
| parent account | cuenta padre | |
| journal entry, entry, transaction (journal) | asiento | "Transaction" in the ledger UI is always an entry |
| posting (entry line) | apunte | "Postings on Control Accounts" = Apuntes en cuentas de control |
| line | línea | |
| journal | diario | |
| general ledger, ledger | libro mayor | |
| sub-ledger | libro auxiliar | |
| trial balance | balance de sumas y saldos | |
| balance sheet | balance | |
| profit & loss / income statement | (cuenta de) pérdidas y ganancias; abbr. PyG | |
| statement of financial position (HK) | estado de situación financiera | |
| statement of profit or loss (HK) | estado del resultado | |
| statutory statements | estados financieros legales | |
| debit / credit (columns, DR / CR) | debe / haber (D / H) | verbs: cargar / abonar |
| draft | borrador | |
| post / posted | contabilizar / contabilizado | |
| void / voided | anular / anulado | |
| reversal (entry) | contraasiento | |
| book (an invoice), booking | registrar, registro (contable) | kept apart from "post" |
| booking engine | motor de registro | |
| booking defaults | cuentas predeterminadas de registro | |
| gap (line awaiting an account) | línea pendiente | |
| fiscal year, FY | ejercicio, Ej. | |
| year-to-date (YTD) | acumulado del ejercicio | |
| accounting period | periodo contable | |
| close / reopen a period | cerrar / reabrir un periodo | |
| year-end closing entry | asiento de cierre del ejercicio | |
| carry-forward entry (report à nouveau) | asiento de traspaso del resultado | |
| retained earnings | resultados de ejercicios anteriores | |
| opening / closing balance | saldo de apertura / saldo de cierre | |
| assets / liabilities / equity | activo / pasivo / patrimonio neto | |
| current / non-current | corriente / no corriente | |
| revenue / expense | ingresos / gastos | |
| gross profit / operating profit / net income | margen bruto / resultado de explotación / resultado neto | |
| fixed assets | inmovilizado | intangible / material / financiero |
| depreciation / accumulated depreciation | amortización / amortización acumulada | |
| book value / salvage value / useful life | valor contable / valor residual / vida útil | |
| linear / declining (method) | lineal / degresivo | |
| cash flow (operating / investing / financing) | flujos de efectivo (explotación / inversión / financiación) | |

## Parties, payments, banking

| English | Spanish | Notes |
|---|---|---|
| vendor / supplier | proveedor | |
| client / customer | cliente | |
| accounts payable / receivable (AP / AR) | cuentas a pagar / cuentas a cobrar; "clientes/proveedores" for AR/AP pairs | |
| aging, age bucket, current (not yet due) | antigüedad de saldos, tramo, no vencido | |
| invoice / bill | factura / factura recibida | |
| payment in / payment out | cobro / pago | |
| payer / payee | pagador / beneficiario | |
| bank statement / bank (statement) line | extracto bancario / movimiento bancario | |
| bank reconciliation | conciliación bancaria | |
| match / unmatch / matched / unmatched | conciliar / deshacer conciliación / conciliado / sin conciliar | |
| match group | grupo de conciliación | |
| bank fee | comisión bancaria | |
| exchange rate | tipo de cambio | "Rate" alone = tipo |
| exchange gain / loss | diferencia positiva / negativa de cambio | PGC 768 / 668 wording |
| exchange clearing account | cuenta puente de cambio | |
| base currency / foreign currency | moneda base / moneda extranjera | |
| rate override (per company) | tipo propio | |
| live rates | tipos en directo | |

## Tax

| English | Spanish | Notes |
|---|---|---|
| VAT | IVA | `{{tax}}` is masculine: "{{tax}} repercutido", "del {{tax}}" |
| output / input VAT | IVA repercutido / IVA soportado | |
| VAT payable / VAT credit (carried forward) | IVA a ingresar / IVA a compensar | generic `{{tax}} payable` = "{{tax}} a pagar" |
| sales tax / consumption tax | impuesto sobre las ventas / impuesto sobre el consumo | |
| surcharge (China) | recargo | urban construction / education / local education |
| corporate income tax (CIT) | Impuesto sobre Sociedades | |
| individual income tax (IIT) | impuesto sobre la renta de las personas físicas (IRPF) | |
| Profits Tax (Hong Kong) | impuesto sobre los beneficios | |
| provisional (prepaid) tax / instalment | pago a cuenta / plazo | |
| demand note / assessment notice | notificación de pago / notificación de liquidación | |
| assessable profit | base imponible | |
| add-back / deduction (tax computation) | aumento / disminución | Spanish IS terms for ajustes extracontables |
| losses brought forward | bases imponibles negativas de ejercicios anteriores | |
| two-tiered / tiered rates | tipos en dos tramos / tipos por tramos | |
| standard rate / reduced rates | tipo general / tipos reducidos | |
| accrual (entry) | (asiento de) devengo | |
| settlement / settle | liquidación / liquidar | |
| filing / filed | declaración / presentado | |
| tax role | función (fiscal) | Role_gnos3 |
| map / mapped | asignar / asignada | |
| tax authority / tax office | administración tributaria | |
| withholding | retención | |
| MPF | MPF (fondo de previsión obligatorio) | kept as a name |
| year of assessment | año de imposición | |

## Expenses, documents, other modules

| English | Spanish | Notes |
|---|---|---|
| expense sheet / reimbursement | hoja de gastos / reembolso | |
| expense receipt | justificante | |
| employee / approver | empleado / aprobador | |
| merchant | comercio | |
| categorization rule (invoice / bank line) | regla de categorización (de facturas / de movimientos bancarios) | |
| business card | tarjeta de visita | |
| job title | cargo | |
| needs review / to review | requiere revisión / por revisar | |
| dashboard | panel | |
| template | plantilla | |
| company | empresa | |
| settings | ajustes | as in the rest of Gnos3 |
| AI | IA | |
| status labels | masculine neutral | Pagado, Vencido, Aprobado, Rechazado, Enviado, Listo, Abierto, Cerrado |

## Statutory statement lines (round 2: CAS small business, HK SME-FRS)

| English | Spanish | Notes |
|---|---|---|
| cash and cash equivalents (货币资金) / cash and bank balances | efectivo y otros activos líquidos equivalentes / caja y bancos | |
| notes receivable / payable | efectos comerciales a cobrar / a pagar | |
| accounts receivable / payable (CAS) | clientes por ventas y prestaciones de servicios / proveedores | |
| trade receivables / payables (HK) | deudores comerciales / acreedores comerciales | |
| prepayments / advances from customers | anticipos a proveedores / anticipos de clientes | |
| inventories; of which: raw materials | existencias; de las cuales: materias primas | |
| construction in progress | inmovilizado en curso | |
| property, plant and equipment | inmovilizado material | |
| employee benefits payable | remuneraciones pendientes de pago | |
| short-term / long-term borrowings | deudas a corto / largo plazo con entidades de crédito | |
| paid-in capital / share capital | capital desembolsado / capital social | |
| capital surplus (资本公积) / surplus reserve (盈余公积) | reservas de capital / reservas legales y voluntarias | |
| retained earnings on a statement (未分配利润) / retained profits (HK) | resultados no distribuidos / beneficios no distribuidos | includes the current year's result |
| non-operating income / expenses (营业外) | ingresos / gastos excepcionales | |
| profit before tax / net profit / profit for the year | resultado antes de impuestos / resultado del ejercicio | |
| net current assets / net assets | activo corriente neto / activo neto | |
