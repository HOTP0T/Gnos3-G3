# Gnos3 business modules — German (de-DE) glossary

## Conventions

- **Form of address: "Sie"** (formal, as Open WebUI's German catalog does), never "du": „Wählen Sie ein Unternehmen“, „Dies kann nicht rückgängig gemacht werden.“ Impersonal phrasing where it reads naturally („Noch kein Unternehmen angelegt“).
- **Buttons and menu actions: infinitive**, object first („Speichern“, „Buchung erstellen“, „Datei hochladen“, „Entwurf löschen“). Titles and labels: noun phrases („Neue Buchung“, „Unternehmenseinstellungen“).
- **Capitalisation**: German rules (all nouns capitalised), otherwise sentence case — never English title case („Gewinn- und Verlustrechnung nach Periode“, not „Gewinn- Und Verlustrechnung Nach Periode“). ALL-CAPS statement totals stay in capitals.
- **Compounds**: one word where German writes one („Kontoauszug“, „Umsatzsteuererklärung“, „Standardeinstellungen“); a hyphen with abbreviations, codes, numbers and product names („USt-Satz“, „K4mi-Tag“, „PDF-Datei“, „CSV-Export“, „EUR-Konto“, „Excel-Vorlage“). With a placeholder: „{{tax}}-Erklärung“, or „Erklärung ({{tax}})“ when the name may be long.
- **Punctuation**: no space before „:“ „?“ „!“ „;“. Quoted UI labels and names in „…“ (U+201E … U+201C). Ellipsis „…“ for progress („Wird geladen…“, „Wird gespeichert…“). "e.g." → „z. B.“, "i.e." → „d. h.“, "etc." → „usw.“, "vs." → „vs.“ / „gegenüber“, "incl." → „inkl.“, "approx." → „ca.“. Dashes: „–“ (en dash with spaces) where English uses "—" as a break.
- **Numbers and dates**: decimal comma, thousands point (1.234,56); dates TT.MM.JJJJ (30.10.2026); months „Januar … Dezember“ (short „Jan., Feb., März …“); percent with a space („19 %“). Ranges „Jan.–März“, „bis“.
- **Debit / credit** → **Soll / Haben**; column headers **S / H** for DR / CR.
- **Placeholders** ({{name}}, {name}, <0>…</0>) stay exactly as given; German word order may move them, never drop or rename them.
- Product names unchanged: Gnos3, K4mi, SmartOffice, Ollama, Open WebUI, Excel, PDF, CSV, ISO currency codes, units.
- Tax names come from the tax kind, never the country's own label: VAT = „USt“ (Umsatzsteuer), GST = „GST“, sales tax = „Sales Tax“, consumption tax = „Verbrauchsteuer“, ICMS = „ICMS“, corporate income tax = „Körperschaftsteuer“, Hong Kong profits tax = „Gewinnsteuer (Profits Tax)“.

## Accounting and finance

| English | German (de-DE) |
|---|---|
| account (ledger) | Konto (Sachkonto) |
| account name / code | Kontobezeichnung / Kontonummer |
| account type | Kontoart |
| chart of accounts | Kontenplan |
| chart template | Kontenplanvorlage |
| control account (with sub-accounts) | Sammelkonto |
| sub-account | Unterkonto |
| detail / leaf account | Einzelkonto (bebuchbares Konto) |
| journal entry / entry / transaction (books) | Buchung (Buchungssatz in formal contexts) |
| line (of an entry) | Buchungszeile |
| journal | Journal |
| ledger / general ledger | Hauptbuch |
| sub-ledger | Nebenbuch |
| trial balance | Summen- und Saldenliste |
| balance sheet | Bilanz |
| profit and loss / income statement / P&L | Gewinn- und Verlustrechnung (GuV) |
| statement of financial position (HK) | Darstellung der Finanzlage |
| statement of profit or loss (HK) | Gewinn- und Verlustrechnung |
| current / non-current assets | kurzfristige / langfristige Vermögenswerte (PCG/HGB layout: Umlaufvermögen / Anlagevermögen) |
| current / non-current liabilities | kurzfristige / langfristige Verbindlichkeiten |
| assets / liabilities | Aktiva / Passiva (an item: Vermögenswert / Verbindlichkeit) |
| equity | Eigenkapital |
| retained earnings | Gewinnrücklagen (Gewinnvortrag) |
| revenue | Umsatzerlöse (short: Erlöse) |
| income (other income) | Erträge (sonstige betriebliche Erträge) |
| expenses (account type, P&L) | Aufwendungen (Aufwand) |
| expenses (the expense-claims tab, `Expenses_tab`) | Spesen |
| cost of sales / COGS | Umsatzkosten |
| net income / profit for the year | Jahresüberschuss (loss: Jahresfehlbetrag) |
| opening balance | Eröffnungssaldo (entries: Eröffnungsbuchung) |
| closing balance | Schlusssaldo |
| balance (of an account) | Saldo |
| debit / credit | Soll / Haben (S / H) |
| draft | Entwurf |
| post / posted | buchen / gebucht |
| book (an invoice) / booking | kontieren / Kontierung |
| booking dialog | Kontierungsdialog |
| booking defaults | Standardkontierung |
| booking engine | Kontierungslogik |
| void / voided | stornieren / storniert (button „Stornieren“) |
| reversal (entry) | Stornobuchung |
| accounting period | Buchungsperiode |
| fiscal year / FY | Geschäftsjahr / GJ |
| year-end closing | Jahresabschluss |
| year to date (YTD) | kumuliert seit Beginn des Geschäftsjahres (short: kum.) |
| close / reopen a period | abschließen / wieder öffnen |
| closing checklist | Abschluss-Checkliste |
| blocker | blockierender Punkt |
| gap (line awaiting an account) | fehlende Kontierung (offene Zeile) |
| bank reconciliation | Bankabstimmung |
| reconcile / reconciliation | abstimmen / Abstimmung |
| match / unmatch / matched | zuordnen / Zuordnung aufheben / zugeordnet |
| match group | Zuordnungsgruppe |
| auto-match | automatische Zuordnung |
| bank statement | Kontoauszug |
| bank line (statement line) | Bankumsatz (pl. Bankumsätze) |
| bank account | Bankkonto |
| counterparty / counterparty account | Gegenpartei / Gegenkonto |
| accounts payable / receivable (AP / AR) | Verbindlichkeiten aus Lieferungen und Leistungen / Forderungen aus Lieferungen und Leistungen (short: Verbindlichkeiten / Forderungen; Kreditoren / Debitoren) |
| AP / AR aging | Fälligkeitsanalyse Kreditoren / Debitoren |
| aging bucket / "Current" bucket | Fälligkeitsband / nicht fällig |
| vendor / supplier | Lieferant |
| customer / client | Kunde |
| bill (supplier invoice) / sales invoice | Eingangsrechnung / Ausgangsrechnung |
| invoice | Rechnung |
| invoice number / date / due date | Rechnungsnummer / Rechnungsdatum / Fälligkeitsdatum |
| net / tax / gross / total amount | Nettobetrag / Steuerbetrag / Bruttobetrag / Gesamtbetrag |
| receipt (expense proof) | Beleg (cash receipt: Quittung) |
| payment | Zahlung |
| payment in / out (inbound / outbound) | Zahlungseingang / Zahlungsausgang |
| payer / payee | Zahler / Zahlungsempfänger |
| payment method | Zahlungsart |
| bank transfer / check / credit card / cash | Überweisung / Scheck / Kreditkarte / Barzahlung |
| currency / base currency | Währung / Basiswährung |
| exchange rate | Wechselkurs |
| exchange difference / gain / loss | Kursdifferenz / Kursgewinn / Kursverlust |
| exchange clearing account | Währungsverrechnungskonto |
| override (company rate) | abweichender Kurs |
| categorization rule | Kontierungsregel |
| bank-line rule | Bankumsatzregel |
| pattern | Suchmuster |
| split (across accounts) | aufteilen / Aufteilung |
| fixed asset / fixed assets | Anlagegut / Anlagevermögen |
| depreciation / accumulated depreciation | Abschreibung / kumulierte Abschreibungen |
| useful life / salvage value / book value | Nutzungsdauer / Restwert / Buchwert |
| linear / declining | linear / degressiv |
| asset register | Anlagenverzeichnis |
| expense sheet | Spesenabrechnung |
| expense (claim line) | Auslage |
| reimbursement | Erstattung |
| employee | Mitarbeiter |
| approve / reject / submit | genehmigen / ablehnen / einreichen |
| company | Unternehmen |
| legal entity name | Firmenname (rechtlicher Name) |
| template | Vorlage |

## Taxes

| English | German (de-DE) |
|---|---|
| VAT | USt (Umsatzsteuer) |
| output / input VAT | Umsatzsteuer / Vorsteuer |
| VAT payable / VAT credit | USt-Zahllast / Vorsteuerüberhang |
| credit brought forward / carried forward | Guthabenvortrag aus der Vorperiode / vorzutragendes Guthaben |
| VAT return / tax return / filing | Umsatzsteuererklärung / Steuererklärung / Erklärung |
| tax rate | Steuersatz |
| tax ID / VAT number | Steuernummer / USt-IdNr. |
| surcharge (China, on VAT) | Zuschlagsteuer |
| urban construction tax | Stadtbau- und Instandhaltungssteuer |
| education surcharge | Bildungszuschlag |
| corporate income tax (CIT) | Körperschaftsteuer (KSt) |
| individual income tax (IIT) | Einkommensteuer (ESt); withheld on salaries: Lohnsteuer |
| profits tax (Hong Kong) | Gewinnsteuer (Profits Tax) |
| provisional tax | Steuervorauszahlung |
| prepaid tax (asset) | vorausbezahlte Steuer |
| assessment notice / demand note | Steuerbescheid / Vorauszahlungsbescheid |
| accrual entry (tax) | Rückstellungsbuchung |
| settlement entry (VAT) | Verrechnungsbuchung |
| settle (a filing) | begleichen |
| add-back / deduction | Hinzurechnung / Kürzung |
| tax computation adjustments | steuerliche Korrekturen |
| assessable profit | zu versteuernder Gewinn |
| losses brought forward | Verlustvorträge |
| two-tier / tiered rates | zweistufiger Steuersatz / Stufentarif |
| tax role mapping / mapped | Zuordnung der Steuerrollen / zugeordnet |
| MPF (HK pension) | MPF (Pflichtvorsorgefonds) |

## Documents (K4mi, as in its German catalog)

| English | German (de-DE) |
|---|---|
| document | Dokument |
| tag | Tag |
| custom field | benutzerdefiniertes Feld |
| correspondent | Korrespondent |
| document type | Dokumenttyp |
| storage path | Speicherpfad |
| workflow | Arbeitsablauf |
| saved view | gespeicherte Ansicht |
| owner | Eigentümer |
| upload | hochladen |
| business card | Visitenkarte |
| needs review / mark reviewed | Prüfung erforderlich / als geprüft markieren |
| extraction | Extraktion (Datenerfassung) |
| knowledge base | Wissensdatenbank |
| personal details | personenbezogene Daten |
| anonymise / pseudonymise | anonymisieren / pseudonymisieren |

## Interface

| English | German (de-DE) |
|---|---|
| settings | Einstellungen |
| dashboard | Dashboard |
| save / cancel | Speichern / Abbrechen |
| delete / remove | Löschen / Entfernen |
| edit | Bearbeiten |
| create / add | Erstellen (records: Anlegen) / Hinzufügen |
| search / filter | Suchen / Filtern (noun: Filter) |
| export / import | Exportieren / Importieren |
| upload / download | Hochladen / Herunterladen |
| apply / confirm | Anwenden / Bestätigen |
| discard / reset / clear | Verwerfen / Zurücksetzen / Leeren |
| close / back / next | Schließen / Zurück / Weiter |
| retry / refresh | Erneut versuchen / Aktualisieren |
| duplicate | Duplizieren |
| preview / details | Vorschau / Details |
| loading… / saving… | Wird geladen… / Wird gespeichert… |
| error / warning | Fehler / Warnung |
| required / optional | erforderlich / optional |
| permission / group / role | Berechtigung / Gruppe / Rolle |
| enabled / disabled | aktiviert / deaktiviert |
