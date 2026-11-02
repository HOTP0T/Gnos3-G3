# Gnos3 business modules — Hungarian (hu-HU) glossary

## Conventions

- **Register**: formal, polite (magázás) in every Gnos3 module, Finances, K4mi and the expense app: "Biztosan törölni szeretné…?", "Adja meg…", "Kérjük, válasszon…". Avoid writing the pronoun "Ön" when the verb form already says it. (Open WebUI's own hu-HU file is informal; our screens are not.)
- **Buttons and menu items**: noun form, as Open WebUI and K4mi do: "Mentés", "Törlés", "Létrehozás", "Könyvelés", "Párosítás". With an object: possessive noun phrase: "Tétel létrehozása", "Számla feltöltése", "Kijelölés törlése".
- **Case**: sentence case (only the first word and proper names capitalised). Month and day names are lowercase (január, hétfő).
- **Quotation marks**: „…” (opening low, closing high); nested: »…«. No space inside the marks.
- **Punctuation**: no space before ":" "?" "!"; ellipsis "…"; dash between clauses " – " (en dash with spaces); ranges without spaces: 2023–2026.
- **Placeholders**: Hungarian suffixes and the article change with the sound that follows, so never glue a suffix to a placeholder. Write "a(z) {{name}}" when the article cannot be known, put the placeholder after a noun that takes the suffix ("a(z) {{name}} nevű cég", "{{count}} tétel"), or use a hyphen with a neutral suffix only when unavoidable. After a number, nouns stay singular: "{{count}} tétel", "3 számla" (never "3 tételek").
- **Numbers**: decimal comma, (non-breaking) space as thousands separator: 1 234 567,89. Percent with no space in running text: 27%. Currency code or symbol after the amount: 1 234,56 EUR, 5 000 Ft.
- **Dates**: year first: 2026. 10. 30. (short) / 2026. október 30. (long); months: 2026. október. "e.g." = "pl."; "etc." = "stb."; "i.e." = "azaz".
- **Debit / credit**: Tartozik / Követel; DR / CR = T / K.
- **Abbreviations**: VAT = áfa (lower case in running text and labels, as NAV writes it; "ÁFA" only inside ALL-CAPS headings). TAO = társasági adó, SZJA = személyi jövedelemadó, écs. = értékcsökkenés.
- **Invoice vs account**: in Hungarian "számla" is the invoice. A ledger account is always "főkönyvi számla" (on crowded tables: "főkönyvi szám" for the code column); a bank account is "bankszámla". Never use bare "számla" for a ledger account.
- **Statement totals in ALL CAPS** stay in capitals.
- **Product names** unchanged: Gnos3, K4mi, SmartOffice, Ollama, Open WebUI, Excel, PDF, CSV; currency codes, units, MPF.

## Terms

| English | Magyar |
|---|---|
| account (ledger) | főkönyvi számla |
| account code | főkönyvi számlaszám |
| account name | főkönyvi számla neve |
| account type | számlatípus |
| chart of accounts | számlatükör |
| control account (with sub-accounts) | gyűjtőszámla |
| sub-account | alszámla |
| detail / leaf account | analitikus számla |
| journal entry / entry / transaction (accounting) | könyvelési tétel (short: tétel) |
| entry line | tételsor |
| journal | napló |
| general ledger | főkönyv |
| sub-ledger | analitika (analitikus nyilvántartás) |
| trial balance | főkönyvi kivonat |
| balance sheet | mérleg |
| profit and loss / income statement | eredménykimutatás |
| statement of financial position (HK) | pénzügyi helyzet kimutatása |
| statement of profit or loss (HK) | eredménykimutatás |
| assets / liabilities | eszközök / források (kötelezettségek) |
| current / non-current assets | forgóeszközök / befektetett eszközök |
| current / non-current liabilities | rövid / hosszú lejáratú kötelezettségek |
| equity | saját tőke |
| retained earnings | eredménytartalék |
| revenue / income | árbevétel / bevétel |
| expense (account type, P&L) | költség (ráfordítás) |
| cost of sales | értékesítés közvetlen költségei |
| fiscal year / FY | üzleti év / ÜÉ |
| period / accounting period | időszak / könyvelési időszak |
| year to date (YTD) | év elejétől (halmozott) |
| year-end closing | évzárás |
| close / reopen a period | időszak lezárása / újranyitása |
| closing checklist | zárási ellenőrzőlista |
| opening balance | nyitó egyenleg |
| closing balance | záró egyenleg |
| balance | egyenleg |
| debit / credit | tartozik / követel (T / K) |
| draft | piszkozat |
| post / posted | könyvelés / könyvelt |
| book (an invoice) / booking | kontírozás / kontírozott |
| booking defaults | alapértelmezett kontírozás |
| booking engine | kontírozó motor |
| gap (line awaiting an account) | kontírozatlan sor |
| blocker | akadály |
| void / voided | érvénytelenítés / érvénytelenített |
| reversal (entry) | sztornó tétel |
| carry-forward entry | eredménytartalék-átvezetés |
| invoice | számla |
| bill (supplier invoice) | bejövő (szállítói) számla |
| sales invoice | kimenő (vevői) számla |
| receipt (retail) | nyugta |
| receipt (supporting document of an expense) | bizonylat |
| payment | fizetés |
| payment in / out | bejövő / kimenő fizetés |
| payment method | fizetési mód |
| bank transfer / check / credit card / cash | átutalás / csekk / bankkártya / készpénz |
| payer / payee | fizető fél / kedvezményezett |
| bank account | bankszámla |
| bank statement | bankszámlakivonat |
| bank line | kivonattétel |
| bank reconciliation | bankegyeztetés |
| reconciliation | egyeztetés |
| match / unmatch / matched | párosítás / párosítás bontása / párosított |
| auto-match | automatikus párosítás |
| match group | párosítási csoport |
| allocated amount | hozzárendelt összeg |
| counterparty | partner |
| counterparty account | ellenszámla |
| supplier / vendor | szállító |
| customer / client | vevő |
| accounts payable / receivable | szállítói kötelezettségek / vevőkövetelések |
| AP / AR aging | szállítói / vevői korosítás |
| aging bucket / "Current" bucket | korosítási sáv / nem lejárt |
| due date | fizetési határidő |
| currency | pénznem |
| base currency | alap pénznem |
| exchange rate | árfolyam |
| exchange difference / gain / loss | árfolyam-különbözet / árfolyamnyereség / árfolyamveszteség |
| exchange clearing account | árfolyam-elszámolási technikai számla |
| rate override (company) | egyedi árfolyam |
| VAT | áfa |
| output / input VAT | fizetendő áfa / levonható áfa |
| VAT payable / VAT credit | befizetendő áfa / visszaigényelhető áfa (áfa-követelés) |
| credit brought / carried forward | előző időszakról áthozott / következő időszakra átvitt követelés |
| GST / GST-HST | GST / GST-HST (forgalmi adó) |
| sales tax / consumption tax | forgalmi adó / fogyasztási adó |
| surcharge (China, on VAT) | pótadó |
| urban construction tax / education surcharge | városfejlesztési adó / oktatási pótadó |
| corporate income tax (CIT) | társasági adó (TAO) |
| individual income tax (IIT) | személyi jövedelemadó (SZJA) |
| profits tax (Hong Kong) | nyereségadó |
| provisional tax | adóelőleg |
| prepaid tax (asset) | előre fizetett adó |
| assessment notice / demand note | adómegállapító határozat / fizetési értesítő |
| tax return / filing | bevallás |
| accrual entry (tax) | adó előírása (előírási tétel) |
| settlement entry (VAT) | áfa-elszámolási tétel |
| settle (a filing) | rendezés |
| add-back / deduction | adóalap-növelő / adóalap-csökkentő tétel |
| tax computation adjustments | adóalap-módosító tételek |
| assessable profit | adóalap |
| losses brought forward | elhatárolt veszteség |
| two-tier / tiered rates | kétkulcsos / sávos adómérték |
| tax role mapping / mapped | adószerep-hozzárendelés / hozzárendelt |
| categorization rule | kategorizálási szabály |
| bank-line rule | kivonattétel-szabály |
| pattern | minta |
| split (across accounts) | felosztás |
| fixed asset | tárgyi eszköz |
| depreciation / accumulated depreciation | értékcsökkenés / halmozott értékcsökkenés |
| useful life / salvage value / book value | hasznos élettartam / maradványérték / nettó könyv szerinti érték |
| linear / declining | lineáris / degresszív |
| asset register | tárgyieszköz-nyilvántartás |
| expense sheet | költségelszámolás |
| expense claim / reimbursement | költségtérítés / visszatérítés |
| employee | munkavállaló |
| approve / reject / submit | jóváhagyás / elutasítás / beküldés |
| company | cég |
| legal entity name | hivatalos cégnév |
| template | sablon |
| business card | névjegykártya |
| needs review / mark reviewed | ellenőrzésre vár / ellenőrzöttnek jelölés |
| extraction | adatkinyerés |
| confidence | megbízhatóság |
| document | dokumentum |
| tag / K4mi tag | címke / K4mi-címke |
| custom field | egyéni mező |
| correspondent | levelező partner |
| document type | dokumentumtípus |
| storage path | tárolási útvonal |
| archive serial number | archívum sorszáma |
| owner | tulajdonos |
| workflow | munkafolyamat |
| upload / download | feltöltés / letöltés |
| import / export | importálás / exportálás |
| settings | beállítások |
| dashboard | irányítópult |
| save / cancel | mentés / mégse |
| delete / remove | törlés / eltávolítás |
| edit | szerkesztés |
| create / add | létrehozás / hozzáadás |
| search / filter | keresés / szűrés (the filter control: szűrő) |
| apply / confirm | alkalmazás / megerősítés |
| reset / clear | visszaállítás / törlés |
| refresh | frissítés |
| loading… | betöltés… |
| error / warning | hiba / figyelmeztetés |
| permissions / group | engedélyek / csoport |
| status | állapot |
| preview | előnézet |
| anonymise | anonimizálás |

## Expenses: two senses

- expenses (account type, P&L, dashboards) → költségek
- expenses (the expense-claims tab / settings group, key `Expenses_tab`) → költségelszámolások
