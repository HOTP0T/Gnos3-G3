# Gnos3 business modules — Greek (el-GR) glossary

## Conventions

- **Form of address: plural of politeness ("εσείς")**: "Επιλέξτε εταιρεία", "Δεν μπορείτε να αναιρέσετε αυτή την ενέργεια". Never the singular "εσύ". Impersonal phrasing is fine where it reads naturally ("Δεν υπάρχουν ακόμη εταιρείες").
- **Buttons and menu actions: verbal noun** (as the existing Open WebUI Greek catalog does): "Αποθήκευση", "Διαγραφή", "Δημιουργία εγγραφής", "Ανέβασμα αρχείου", "Εξαγωγή σε Excel". Instructions in running text use the polite imperative ("Επιλέξτε…", "Ανεβάστε…", "Συμπληρώστε…").
- **Sentence case**: only the first word and proper names take a capital ("Κατάσταση αποτελεσμάτων ανά περίοδο"). Words written ALL CAPS drop their accents (ΣΥΝΟΛΟ ΕΝΕΡΓΗΤΙΚΟΥ, not ΣΎΝΟΛΟ); statement totals that are in capitals in English stay in capitals.
- **Punctuation**: the Greek question mark is ";" ("Διαγραφή της εταιρείας;"). Quoted UI labels and names in « » («Αποθήκευση»). Ellipsis "…" for progress ("Φόρτωση…", "Αποθήκευση…"). No space before ":" or ";". "e.g." → "π.χ.", "i.e." → "δηλ.", "etc." → "κ.λπ.", "vs." → "έναντι".
- **Spelling**: "καταχώριση" (not "καταχώρηση"), "ανάληψη", "εταιρεία", "πρότυπο". Final ν kept or dropped by the standard rule (την εταιρεία, τη χρήση).
- **Numbers and dates**: decimal comma, thousands dot (1.234,56); dates dd/mm/yyyy (30/10/2026); month and weekday names lower case in running text (οκτώβριος, Δευ/Τρι). Percent without space (24%). The code formats numbers and dates; translations never hard-code a format.
- **DR / CR** → **Χ / Π** in column headers ("Χρέωση" / "Πίστωση" written out elsewhere).
- **Placeholders** ({{name}}, {name}, <0>…</0>) stay exactly as given; Greek word order may move them, never drop or rename them. A `{{tax}}` / `{tax}` filled with a tax name (ΦΠΑ, GST, φόρος κερδών…) is used without an article where possible ("Δήλωση {{tax}}", "Λογαριασμός {{tax}}").
- **Product names stay as they are**: Gnos3, K4mi, SmartOffice, Finances, Ollama, Open WebUI, Excel, PDF, CSV, ISO codes, currency codes, units.

## Accounting and finance

| English | Greek (el-GR) |
|---|---|
| account (ledger) | λογαριασμός |
| account name / code | όνομα λογαριασμού / κωδικός λογαριασμού |
| chart of accounts | λογιστικό σχέδιο |
| account type | τύπος λογαριασμού |
| control account (with sub-accounts) | συγκεντρωτικός λογαριασμός |
| sub-account | υπολογαριασμός |
| detail / leaf account | αναλυτικός λογαριασμός (τελευταίου βαθμού) |
| journal entry / entry / transaction (books) | λογιστική εγγραφή / εγγραφή |
| line (of an entry) | γραμμή εγγραφής |
| journal | ημερολόγιο |
| general ledger | γενικό καθολικό |
| sub-ledger | αναλυτικό καθολικό |
| trial balance | ισοζύγιο (γενικό ισοζύγιο) |
| balance sheet | ισολογισμός |
| profit and loss / income statement / P&L | κατάσταση αποτελεσμάτων |
| statement of financial position (HK) | κατάσταση χρηματοοικονομικής θέσης |
| statement of profit or loss (HK) | κατάσταση αποτελεσμάτων |
| current / non-current assets | κυκλοφορούντα / μη κυκλοφορούντα περιουσιακά στοιχεία |
| current / non-current liabilities | βραχυπρόθεσμες / μακροπρόθεσμες υποχρεώσεις |
| assets / liabilities | ενεργητικό (περιουσιακά στοιχεία) / υποχρεώσεις |
| equity | ίδια κεφάλαια |
| revenue / income | έσοδα |
| expenses (account type, P&L, dashboards) | έξοδα |
| cost of sales / gross profit | κόστος πωληθέντων / μικτό κέρδος |
| net income / net profit | καθαρό αποτέλεσμα / καθαρά κέρδη |
| retained earnings | αποτελέσματα εις νέον |
| opening balance | υπόλοιπο έναρξης |
| closing balance | υπόλοιπο κλεισίματος |
| balance | υπόλοιπο |
| debit / credit | χρέωση / πίστωση (columns: Χ / Π) |
| draft | πρόχειρο |
| post / posted | καταχώριση / καταχωρισμένη (button: «Καταχώριση») |
| book (an invoice), booking | λογιστικοποίηση, λογιστικοποίηση τιμολογίου |
| booking defaults | προεπιλογές λογιστικοποίησης |
| void / voided | ακύρωση / ακυρωμένη (button: «Ακύρωση εγγραφής», never bare «Ακύρωση», which is Cancel) |
| reversal (entry) | αντιλογισμός (εγγραφή αντιλογισμού) |
| accounting period / period | λογιστική περίοδος / περίοδος |
| fiscal year / FY | χρήση (διαχειριστική χρήση) / Χρ. |
| year-end closing | κλείσιμο χρήσης |
| year to date (YTD) | από την αρχή της χρήσης (σωρευτικά) |
| close / reopen a period | κλείσιμο / επαναφορά (άνοιγμα) περιόδου |
| closing checklist | έλεγχοι κλεισίματος |
| blocker | εμπόδιο (ζήτημα που εμποδίζει) |
| gap (line awaiting an account) | εκκρεμότητα (γραμμή σε εκκρεμότητα) |
| bank account | τραπεζικός λογαριασμός |
| bank statement | αντίγραφο κίνησης (τραπεζικού λογαριασμού) |
| bank line | τραπεζική κίνηση |
| bank reconciliation | τραπεζική συμφωνία |
| match / unmatch / matched | αντιστοίχιση / κατάργηση αντιστοίχισης / αντιστοιχισμένη |
| match group | ομάδα αντιστοίχισης |
| counterparty | αντισυμβαλλόμενος |
| accounts payable / receivable | υποχρεώσεις προς προμηθευτές / απαιτήσεις από πελάτες |
| AP / AR aging | ενηλικίωση υποχρεώσεων / απαιτήσεων |
| aging bucket / "Current" bucket | κλιμάκιο / μη ληξιπρόθεσμα |
| supplier / vendor | προμηθευτής |
| customer / client | πελάτης |
| invoice | τιμολόγιο |
| bill (supplier invoice) | τιμολόγιο αγοράς (προμηθευτή) |
| receipt | απόδειξη |
| payment | πληρωμή |
| payment in / out | είσπραξη / πληρωμή |
| payer / payee | πληρωτής / δικαιούχος |
| payment method | τρόπος πληρωμής |
| bank transfer / check / credit card / cash | τραπεζική μεταφορά / επιταγή / πιστωτική κάρτα / μετρητά |
| currency | νόμισμα |
| base currency | νόμισμα βάσης |
| exchange rate | συναλλαγματική ισοτιμία (short: ισοτιμία) |
| exchange difference / gain / loss | συναλλαγματική διαφορά / κέρδος / ζημία από συναλλαγματικές διαφορές |
| exchange clearing account | ενδιάμεσος λογαριασμός συναλλάγματος |
| override (company rate) | ειδική ισοτιμία εταιρείας |
| categorization rule | κανόνας κατηγοριοποίησης |
| bank-line rule | κανόνας τραπεζικών κινήσεων |
| pattern | μοτίβο |
| split (across accounts) | επιμερισμός, επιμερίζω |
| fixed asset | πάγιο |
| depreciation / accumulated depreciation | απόσβεση / σωρευμένες αποσβέσεις |
| useful life / salvage value / book value | ωφέλιμη ζωή / υπολειμματική αξία / αναπόσβεστη αξία |
| linear / declining | σταθερή / φθίνουσα μέθοδος |
| asset register | μητρώο παγίων |
| expense sheet / reimbursement sheet | κατάσταση εξόδων |
| expenses (the expense-claims tab, key `Expenses_tab`) | καταστάσεις εξόδων |
| expense receipt | παραστατικό εξόδου |
| reimbursement | αποζημίωση (επιστροφή εξόδων) |
| employee | εργαζόμενος |
| approve / reject / submit | έγκριση / απόρριψη / υποβολή |
| VAT | ΦΠΑ |
| GST / GST-HST / sales tax / consumption tax | GST / GST-HST / φόρος επί των πωλήσεων / φόρος κατανάλωσης |
| output / input VAT | ΦΠΑ εκροών / ΦΠΑ εισροών |
| VAT payable / VAT credit | ΦΠΑ προς απόδοση / πιστωτικό υπόλοιπο ΦΠΑ |
| credit brought / carried forward | πιστωτικό υπόλοιπο προηγούμενης περιόδου / προς μεταφορά |
| surcharge (China, on VAT) | πρόσθετος φόρος |
| corporate income tax (CIT) | φόρος εισοδήματος νομικών προσώπων (short: φόρος εισοδήματος) |
| individual income tax (IIT) | φόρος εισοδήματος φυσικών προσώπων |
| profits tax (Hong Kong) | φόρος κερδών |
| provisional tax | προκαταβολή φόρου |
| prepaid tax (asset) | προπληρωμένος φόρος |
| assessment notice / demand note | εκκαθαριστικό σημείωμα / ειδοποίηση πληρωμής |
| tax return / filing | φορολογική δήλωση / δήλωση |
| accrual entry (tax) | εγγραφή πρόβλεψης φόρου |
| settlement entry (VAT) | εγγραφή εκκαθάρισης |
| settle (a filing) | εξόφληση |
| add-back / deduction | προσαύξηση / μείωση (φορολογικές αναμορφώσεις) |
| tax computation adjustments | φορολογικές αναμορφώσεις |
| assessable profit | φορολογητέο κέρδος |
| losses brought forward | μεταφερόμενες ζημίες |
| two-tier / tiered rates | συντελεστές δύο κλιμακίων / κλιμακωτοί συντελεστές |
| tax role mapping / mapped | αντιστοίχιση / αντιστοιχισμένος |
| template | πρότυπο |
| company | εταιρεία |
| legal entity name | επωνυμία |
| tax ID / VAT number | ΑΦΜ |

## Documents (K4mi)

| English | Greek (el-GR) |
|---|---|
| document | έγγραφο |
| tag | ετικέτα |
| custom field | προσαρμοσμένο πεδίο |
| correspondent | ανταποκριτής |
| document type | τύπος εγγράφου |
| storage path | διαδρομή αποθήκευσης |
| workflow | ροή εργασίας |
| upload | ανέβασμα (verb: ανεβάστε) |
| owner | ιδιοκτήτης |
| business card | επαγγελματική κάρτα |
| needs review / mark reviewed | προς έλεγχο / σήμανση ως ελεγμένο |
| extraction | εξαγωγή δεδομένων |
| reprocess | επανεπεξεργασία |
| K4mi tag | ετικέτα K4mi |

## UI words

| English | Greek (el-GR) |
|---|---|
| settings | Ρυθμίσεις |
| dashboard | Πίνακας ελέγχου |
| save | Αποθήκευση |
| cancel | Ακύρωση |
| delete | Διαγραφή |
| edit | Επεξεργασία |
| search | Αναζήτηση |
| filter | Φίλτρο / φιλτράρισμα |
| export / import | Εξαγωγή / Εισαγωγή |
| download | Λήψη |
| apply | Εφαρμογή |
| confirm | Επιβεβαίωση |
| loading… | Φόρτωση… |
| error | Σφάλμα |
| status | Κατάσταση |
| date | Ημερομηνία |
| amount | Ποσό |
| total | Σύνολο |
| close (a dialog) | Κλείσιμο |
| next / previous | Επόμενο / Προηγούμενο |
| refresh | Ανανέωση |
| retry | Επανάληψη |
| permissions | Δικαιώματα |
| group / user | ομάδα / χρήστης |
| admin / superadmin | διαχειριστής / υπερδιαχειριστής |
| workspace | Χώρος εργασίας |
| knowledge base | βάση γνώσεων |
| model | μοντέλο |
| chat | συνομιλία |
