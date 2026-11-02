# Gnos3 business modules — Italian (it-IT) glossary

## Conventions

- **Form of address: formal, and impersonal wherever possible.** Instructions and hints use the infinitive or an impersonal form ("Selezionare una società", "Non è possibile annullare l'operazione", "Nessuna società creata"). When the reader must be addressed directly, use **Lei** (third person: "Non dispone dell'autorizzazione", "Può modificarlo in seguito"), never "tu".
- **Buttons and menu actions: short imperative, as Open WebUI and K4mi already do** ("Salva", "Annulla", "Elimina", "Crea scrittura", "Carica file", "Contabilizza"). Titles and labels: noun phrases ("Nuova scrittura", "Impostazioni della società").
- **Sentence case**: only the first word and proper names get a capital ("Conto economico per periodo", "Flussi di lavoro"). ALL-CAPS statement totals stay in capitals.
- **Punctuation**: no space before ":" "?" "!" ";". Quoted UI labels and names in “…” (typographic double quotes). Ellipsis "…" for progress ("Caricamento…", "Salvataggio…"). "e.g." → "ad es.", "i.e." → "ossia", "etc." → "ecc.", "vs." → "rispetto a".
- **Numbers and dates**: decimal comma, thousands point (1.234,56); dates dd/mm/yyyy (30/10/2026); month and weekday names lower case (ottobre, lun, mar); percent without a space (22%). Currency codes after the amount ("1.234,56 EUR").
- **DR / CR** → **D / A** (Dare / Avere) in column headers; "Dare" / "Avere" written out elsewhere.
- **Elision and articles**: "l'IVA", "dell'esercizio", "un'imposta". With a placeholder holding a tax name (`{{tax}}`, `{tax}`) avoid the article or put the name in apposition ("Dichiarazione {{tax}}", "Aliquota {{tax}}"), so it reads for IVA, GST and income taxes alike.
- **Placeholders** ({{name}}, {name}, <0>…</0>) stay exactly as given; Italian word order may move them, never drop or rename them.
- **Product names stay**: Gnos3, K4mi, SmartOffice, Finances, Ollama, Open WebUI, Excel, PDF, CSV, currency codes, units.

## Accounting and finance

| English | Italian (it-IT) |
|---|---|
| account (ledger; key `Account_gnos3`) | conto |
| account name / account code | descrizione del conto / codice conto |
| chart of accounts | piano dei conti |
| account type | tipo di conto |
| control account (has sub-accounts) | conto di raggruppamento |
| sub-account | sottoconto |
| detail / leaf account | conto di dettaglio |
| journal entry / entry / transaction (books) | scrittura (contabile) |
| line (of an entry) | riga |
| journal | libro giornale |
| ledger / general ledger | libro mastro |
| sub-ledger | partitario |
| trial balance | bilancio di verifica |
| balance sheet | stato patrimoniale |
| profit and loss / income statement / P&L | conto economico |
| statement of financial position (HK) | prospetto della situazione patrimoniale-finanziaria |
| statement of profit or loss (HK) | prospetto dell'utile (perdita) d'esercizio |
| assets / liabilities | attività / passività |
| current / non-current assets | attività correnti / non correnti |
| current / non-current liabilities | passività correnti / non correnti |
| equity | patrimonio netto |
| retained earnings | utili portati a nuovo |
| revenue / income | ricavi / proventi |
| expenses (account type, P&L, dashboards) | costi |
| expenses (expense-claims tab, key `Expenses_tab`) | note spese |
| cost of sales | costo del venduto |
| gross profit / net income | utile lordo / utile netto (risultato netto) |
| opening balance | saldo iniziale |
| closing balance | saldo finale |
| debit / credit | dare / avere |
| draft | bozza |
| post / posted | contabilizzare / contabilizzata |
| book (an invoice) / booking | registrare / registrazione |
| booking defaults | conti predefiniti di registrazione |
| booking engine | motore di registrazione |
| void / voided | annullare / annullata (button: "Annulla scrittura", never a bare "Annulla" = Cancel) |
| reversal (entry) | storno |
| accounting period | periodo contabile |
| fiscal year / FY | esercizio / Es. |
| year-end closing | chiusura dell'esercizio |
| year to date (YTD) | progressivo d'esercizio |
| close / reopen a period | chiudere / riaprire |
| closing checklist | controlli di chiusura |
| blocker | elemento bloccante |
| gap (line awaiting an account) | riga in sospeso |
| bank reconciliation | riconciliazione bancaria |
| match / unmatch / matched | abbinare / annullare l'abbinamento / abbinata |
| match group | gruppo di abbinamento |
| bank statement | estratto conto bancario |
| bank line | movimento bancario |
| counterparty (party) / counterparty account or line | controparte / conto o riga di contropartita |
| accounts payable / receivable | debiti verso fornitori / crediti verso clienti |
| AP / AR aging | scadenzario fornitori / clienti |
| aging bucket / "Current" bucket | fascia di scadenza / non scaduto |
| vendor / supplier | fornitore |
| customer / client | cliente |
| bill (supplier invoice) | fattura passiva |
| invoice / credit note | fattura / nota di credito |
| due date | scadenza |
| receipt (expense proof) | giustificativo (ricevuta / scontrino on the expense app) |
| payment / payment in / payment out | pagamento / incasso / pagamento |
| payer / payee | pagatore / beneficiario |
| payment method | metodo di pagamento |
| bank transfer / check / credit card / cash | bonifico bancario / assegno / carta di credito / contanti |
| currency / base currency | valuta / valuta di base |
| exchange rate | tasso di cambio |
| exchange difference / gain / loss | differenza di cambio / utile su cambi / perdita su cambi |
| exchange clearing account | conto transitorio cambi |
| rate override (company) | tasso specifico |
| categorization rule | regola di categorizzazione |
| bank-line rule | regola sui movimenti bancari |
| pattern (rule) | criterio |
| split (across accounts) | ripartire / ripartizione |
| fixed asset / asset register | cespite / registro dei cespiti |
| depreciation / accumulated depreciation | ammortamento / fondo ammortamento |
| depreciation charge | quota di ammortamento |
| useful life / salvage value / book value | vita utile / valore residuo / valore netto contabile |
| straight-line / declining balance | a quote costanti / a quote decrescenti |
| expense sheet / reimbursement sheet | nota spese |
| reimbursement | rimborso |
| employee | dipendente |
| trip (expense app) / merchant / approver | trasferta / esercente / approvatore |
| portal login | accesso al portale |
| status words (approved, submitted, paid, voided…) | feminine, agreeing with nota spese / spesa / scrittura: approvata, inviata, pagata, annullata |
| approve / reject / submit | approvare / rifiutare / inviare |
| company | società |
| legal name | ragione sociale |
| template | modello |
| built-in (category, template) | integrato |
| statutory statements | prospetti di bilancio obbligatori |

## Taxes

| English | Italian (it-IT) |
|---|---|
| VAT / GST / GST-HST | IVA / GST / GST-HST |
| sales tax / consumption tax | imposta sulle vendite / imposta sui consumi |
| output VAT / input VAT | IVA a debito / IVA a credito |
| VAT payable / VAT credit | IVA da versare / credito IVA |
| credit brought forward / carried forward | credito del periodo precedente / credito da riportare |
| VAT settlement (entry) | liquidazione IVA (scrittura di liquidazione) |
| surcharge (China, on VAT) | addizionale |
| tax rate | aliquota |
| corporate income tax (CIT) | imposta sul reddito delle società (IRES) |
| individual income tax (IIT) | imposta sul reddito delle persone fisiche (IRPEF) |
| profits tax (Hong Kong) | imposta sugli utili |
| provisional tax / prepaid tax | acconto d'imposta / acconti d'imposta versati |
| assessment notice / demand note | avviso di accertamento / avviso di pagamento |
| tax return / filing | dichiarazione |
| accrual entry (tax) | scrittura di accantonamento |
| settle (a filing) | liquidare |
| add-back / deduction (tax computation) | variazione in aumento / variazione in diminuzione |
| tax computation adjustments | variazioni fiscali |
| assessable profit | reddito imponibile |
| losses brought forward | perdite fiscali pregresse |
| two-tier / tiered rates | aliquote a due scaglioni / aliquote a scaglioni |
| tax role mapping / mapped | associazione / associato |

## Documents (K4mi) and modules

| English | Italian (it-IT) |
|---|---|
| document / documents | documento / documenti |
| tag (K4mi) | etichetta (as K4mi's Italian catalog) |
| custom field | campo personalizzato |
| correspondent | corrispondente |
| document type | tipo di documento |
| storage path | percorso di archiviazione |
| workflow | flusso di lavoro |
| owner | proprietario |
| business card | biglietto da visita |
| needs review / mark reviewed | da verificare / segna come verificato |
| extraction / reprocess | estrazione / rielabora |
| confidence | affidabilità |
| data source | origine dati |
| knowledge base | knowledge base |
| Anonymiser / anonymise | Anonimizzatore / anonimizzare |

## Interface words

| English | Italian (it-IT) |
|---|---|
| settings | Impostazioni |
| dashboard | Dashboard |
| save / cancel | Salva / Annulla |
| delete / remove | Elimina / Rimuovi |
| edit | Modifica |
| create / add | Crea / Aggiungi |
| search / filter | Cerca / Filtra |
| export / import | Esporta / Importa |
| upload / download | Carica / Scarica |
| apply / confirm | Applica / Conferma |
| close / back / next / previous | Chiudi / Indietro / Avanti / Precedente |
| refresh / retry | Aggiorna / Riprova |
| loading… / saving… | Caricamento… / Salvataggio… |
| error / warning | Errore / Avviso |
| status | stato |
| permissions / group | permessi / gruppo |
| user / admin / superadmin | utente / amministratore / superamministratore |
| page X of Y | pagina X di Y |
