# Gnos3 business modules — Polish (pl-PL) glossary

## Conventions

- **Register**: neutral-professional, as in Polish business software. Never "Pan/Pani", avoid "Ty/Twój" pronouns: use impersonal forms ("Nie można zapisać zapisu", "Należy wybrać konto", "Wybrano 3 pozycje") or the short imperative in instructions ("Wybierz konto", "Wpisz kurs") — the same imperative Open WebUI pl-PL and K4mi pl-PL already use.
- **Buttons and menu items**: 2nd-person imperative, short ("Zapisz", "Utwórz zapis", "Zaksięguj", "Unieważnij zapis"). Tab and column titles are nouns ("Ustawienia", "Zapisy", "Kwota").
- **Case**: sentence case — only the first word and proper names capitalised ("Domyślne konta księgowania"). Month and weekday names lowercase in running text. ALL-CAPS statement totals (AKTYWA, PASYWA) stay in capitals.
- **Punctuation**: no space before ":" "?" "!"; Polish quotes „…” for quoted UI labels and names (nested: «…»); spaced en dash " – " for asides; "…" (one character) for "Ładowanie…"; "np." for "e.g.", "tj." for "i.e.", "itd." / "itp." for "etc."; arrows "→" in menu paths stay ("Ustawienia → Kursy walut").
- **Numbers and dates**: decimal comma, space (non-breaking) as thousands separator (1 234,56); dates DD.MM.RRRR (30.10.2026); "15%" written without a space (Polish typographic usage). Currency codes (PLN, EUR, USD, HKD) and units stay as they are.
- **Wn / Ma**: debit = Winien (Wn), credit = Ma. Column headers "Wn" / "Ma"; DR / CR in the source → Wn / Ma. "Debit balance" = saldo debetowe (Wn), "credit balance" = saldo kredytowe (Ma).
- **Placeholders**: Polish declines nouns; build sentences so a `{{name}}` / `{name}` stays in the nominative — apposition after a noun ("konto {{code}}", "firma „{{name}}”") or after a colon ("Brak konta: {{code}}").
- **Counts**: Polish has three plural forms (1 / 2–4 / 5+, with 12–14 → 5+). With a bare `{{count}} rows` prefer a neutral form "Wiersze: {{count}}" / "Liczba wierszy: {{count}}"; when a key is explicitly singular or plural, use the matching form, with the 5+ form (genitive plural) as the default plural.
- **Tax names** inserted as `{{tax}}` / `{tax}` (VAT, GST, podatek od sprzedaży, podatek konsumpcyjny, CIT, podatek od zysków) are all masculine in Polish — agreement in the masculine ("{{tax}} należny", "{{tax}} do zapłaty"); prefer "deklaracja ({{tax}})" or "deklaracja {{tax}}" to declining the placeholder.
- **Product names** stay: Gnos3, K4mi, SmartOffice, Ollama, Open WebUI, Excel, PDF, CSV.
- **Delete vs Remove**: Delete = Usuń (destroys data), Remove = Usuń / Odłącz (takes out of a list, unassigns: "Odłącz od firmy"). Void = Unieważnij (never "Anuluj", which is Cancel). Reverse = Stornuj.

## Terms

| English | Polish |
|---|---|
| account (ledger) — `Account_gnos3` | konto (księgowe) |
| account name | nazwa konta |
| account code / number | numer konta (symbol konta) |
| chart of accounts | plan kont |
| control account (with sub-accounts) | konto syntetyczne |
| sub-account | konto analityczne (subkonto) |
| detail / leaf account | konto analityczne najniższego poziomu (konto końcowe) |
| account type | typ konta |
| assets / liabilities / equity | aktywa / zobowiązania / kapitał własny |
| revenue / income | przychody |
| expenses (account type, P&L, dashboards) | koszty |
| expenses (expense-claims tab, key `Expenses_tab`) | wydatki (rozliczenia wydatków) |
| journal entry / entry / transaction | zapis księgowy / zapis |
| journal | dziennik |
| entry line | pozycja zapisu |
| voucher | dowód księgowy |
| reference (entry) | numer dowodu |
| general ledger | księga główna |
| sub-ledger | księga pomocnicza |
| trial balance | zestawienie obrotów i sald |
| balance sheet | bilans |
| profit and loss / income statement / P&L | rachunek zysków i strat |
| statement of financial position (HK) | sprawozdanie z sytuacji finansowej |
| statement of profit or loss (HK) | sprawozdanie z zysków lub strat |
| current / non-current assets | aktywa obrotowe / aktywa trwałe |
| current / non-current liabilities | zobowiązania krótkoterminowe / długoterminowe |
| retained earnings | zyski zatrzymane |
| cost of sales / gross profit | koszt własny sprzedaży / zysk brutto ze sprzedaży |
| operating profit / net income | zysk z działalności operacyjnej / zysk netto |
| profit before taxation | zysk przed opodatkowaniem |
| administrative expenses / finance costs | koszty ogólnego zarządu / koszty finansowe |
| opening balance | saldo początkowe (entries: bilans otwarcia, BO) |
| closing balance | saldo końcowe |
| debit / credit | Winien (Wn) / Ma |
| movement (TB column) | obroty |
| draft | wersja robocza |
| post / posted | zaksięguj / zaksięgowany |
| book (an invoice) / booking | zaksięguj / księgowanie (dekretacja) |
| booking defaults | domyślne konta księgowania |
| booking engine | mechanizm księgowania |
| gap (line awaiting an account) | luka (pozycja bez konta) |
| incomplete (entry with gaps) | niekompletny |
| void / voided | unieważnij / unieważniony |
| reversal (entry) | storno (zapis stornujący) |
| accounting period / period | okres księgowy / okres |
| fiscal year / FY | rok obrotowy / RO |
| year to date (YTD) | narastająco od początku roku |
| year-end closing | zamknięcie roku obrotowego |
| close / reopen a period | zamknij / otwórz ponownie |
| closing checklist | lista kontrolna zamknięcia |
| blocker | przeszkoda blokująca |
| bank reconciliation | uzgodnienie bankowe |
| match / unmatch / matched | dopasuj / cofnij dopasowanie / dopasowany |
| match group | grupa dopasowań |
| auto-match | automatyczne dopasowanie |
| bank statement | wyciąg bankowy |
| bank line / statement line | pozycja wyciągu |
| bank account | rachunek bankowy |
| counterparty | kontrahent |
| accounts payable / receivable | zobowiązania wobec dostawców / należności od odbiorców |
| AP / AR aging | wiekowanie zobowiązań / wiekowanie należności |
| aging bucket / "Current" bucket | przedział wiekowy / bieżące (nieprzeterminowane) |
| vendor / supplier | dostawca |
| customer | odbiorca (klient) |
| client (on an invoice) | nabywca |
| invoice / bill (supplier invoice) | faktura / faktura zakupu |
| sales invoice | faktura sprzedaży |
| receipt (expense) | paragon / dowód zakupu |
| payment | płatność |
| payment in / out | wpływ / wypływ (płatność przychodząca / wychodząca) |
| payer / payee | płatnik / odbiorca płatności |
| payment method | forma płatności |
| bank transfer / check / credit card / cash | przelew / czek / karta kredytowa / gotówka |
| due date | termin płatności |
| overdue | przeterminowany |
| currency / base currency | waluta / waluta bazowa |
| exchange rate | kurs walutowy |
| company rate override | kurs własny firmy |
| exchange difference / gain / loss | różnice kursowe / dodatnie różnice kursowe / ujemne różnice kursowe |
| exchange clearing account | konto rozliczeniowe przewalutowań |
| categorization rule | reguła kategoryzacji |
| bank-line rule | reguła dla pozycji wyciągu |
| pattern | wzorzec |
| split (across accounts) | podział / podziel |
| fixed asset | środek trwały |
| depreciation / accumulated depreciation | amortyzacja / umorzenie |
| depreciation charge | odpis amortyzacyjny |
| useful life / salvage value / book value | okres użytkowania / wartość końcowa / wartość księgowa netto |
| linear / declining | liniowa / degresywna |
| asset register | ewidencja środków trwałych |
| accrual / prepayment | rozliczenie międzyokresowe bierne / czynne |
| expense / expense claim | wydatek |
| expense sheet | rozliczenie wydatków |
| reimbursement | zwrot kosztów |
| employee | pracownik |
| approve / reject / submit | zatwierdź / odrzuć / wyślij do zatwierdzenia |
| VAT / GST / GST-HST | VAT / GST / GST-HST |
| sales tax / consumption tax | podatek od sprzedaży / podatek konsumpcyjny |
| output / input VAT | VAT należny / VAT naliczony |
| VAT payable / VAT credit | VAT do zapłaty / nadwyżka VAT naliczonego |
| credit brought forward / carried forward | nadwyżka z poprzedniego okresu / nadwyżka do przeniesienia |
| surcharge (China, on VAT) | podatek dodatkowy |
| urban construction tax / education surcharge | podatek na utrzymanie i budowę miast / dodatkowa opłata edukacyjna |
| corporate income tax (CIT) | podatek dochodowy od osób prawnych (CIT) |
| individual income tax (IIT) | podatek dochodowy od osób fizycznych (PIT) |
| profits tax (Hong Kong) | podatek od zysków (Profits Tax) |
| provisional tax | zaliczka na podatek |
| prepaid tax (asset) | zapłacone zaliczki na podatek |
| assessment notice / demand note | decyzja wymiarowa / wezwanie do zapłaty |
| tax return / filing | deklaracja (podatkowa) |
| accrual entry (tax) | zapis naliczenia podatku |
| settlement entry (VAT) | zapis rozliczenia |
| settle (a filing) | rozlicz |
| add-back / deduction | doliczenie / odliczenie |
| tax computation adjustments | korekty podatkowe |
| assessable profit | dochód do opodatkowania |
| losses brought forward | straty z lat ubiegłych |
| two-tier / tiered rates | stawka dwustopniowa / stawki progresywne |
| tax role mapping / mapped | przypisanie / przypisane |
| template | szablon |
| company | firma |
| legal entity name | pełna nazwa prawna |
| business card | wizytówka |
| extraction | ekstrakcja (odczyt danych) |
| confidence | pewność |
| needs review / mark reviewed | do weryfikacji / oznacz jako zweryfikowane |
| reprocess | przetwórz ponownie |
| document | dokument |
| tag (K4mi tag) | tag (tag K4mi) |
| custom field | pole niestandardowe |
| correspondent | korespondent |
| document type | typ dokumentu |
| storage path | ścieżka zapisu |
| workflow | proces |
| owner | właściciel |
| anonymiser / anonymise | anonimizator / anonimizuj |
| personal details | dane osobowe |
| decrypt | odszyfruj |
| dashboard | pulpit |
| settings | ustawienia |
| save / cancel / delete / edit | zapisz / anuluj / usuń / edytuj |
| search / filter | szukaj / filtruj (noun: filtr) |
| export / import | eksportuj / importuj (noun: eksport / import) |
| upload / download | prześlij / pobierz |
| apply / confirm | zastosuj / potwierdź |
| loading | Ładowanie… |
| error / warning | błąd / ostrzeżenie |
| group / permission / role | grupa / uprawnienie / rola |
| admin / accountant / viewer | administrator / księgowy / przeglądający |
