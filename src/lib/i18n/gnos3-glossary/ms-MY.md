# Gnos3 business modules — Malay (ms-MY, Bahasa Malaysia) glossary

## Conventions

- **Standard Bahasa Malaysia (DBP spelling), not Indonesian.** Use the Malaysian words: akaun (not akun), invois (not faktur), syarikat (not perusahaan), fail (not berkas), muat naik / muat turun (not unggah / unduh), padam (not hapus), tetapan (not pengaturan), kemas kini (not perbarui), ralat (not galat), carian, e-mel, kata laluan.
- **Form of address: "anda"** (lower case, polite); never "kamu" / "awak". Prefer impersonal or passive phrasing when it reads naturally ("Syarikat belum dicipta", "Tindakan ini tidak boleh dibuat asal").
- **Buttons and menu actions: bare imperative verb** (no *meN-* prefix), object after the verb: "Simpan", "Padam", "Cipta catatan", "Muat naik fail", "Guna penapis". Progress states use *meN-* + "…": "Memuatkan…", "Menyimpan…", "Memuat naik…". Titles and labels are noun phrases ("Catatan baharu", "Tetapan syarikat").
- **Sentence case**: capital only on the first word, proper names and month / day names (Januari, Isnin). ALL-CAPS statement totals stay in capitals.
- **Punctuation**: no space before ":" "?" "!" ";". Quoted UI labels and names in “…”. Ellipsis "…" for progress. "e.g." → "cth.", "i.e." → "iaitu", "etc." → "dsb.", "vs." → "lwn.".
- **Numbers and dates**: Malaysia writes a decimal point and comma thousands (1,234.56); dates dd/mm/yyyy (30/10/2026); "hingga" for ranges ("Jan hingga Mac"); percent without a space (6%). Currency codes before the amount (MYR 1,000.00, EUR 12.50). Months: Januari, Februari, Mac, April, Mei, Jun, Julai, Ogos, September, Oktober, November, Disember.
- **Plurals**: Malay does not inflect; avoid reduplication ("dokumen-dokumen") unless meaning needs it — "{{count}} dokumen", "3 invois". Singular and plural English keys usually get the same Malay text.
- **New / new item**: "baharu" (DBP form), not "baru" in labels ("Catatan baharu", "Syarikat baharu").
- **DR / CR** → **Dt / Kt** in column headers; "Debit" / "Kredit" written out elsewhere.
- **Placeholders** ({{name}}, {name}, <0>, <1/>) stay exactly as given; word order may move them, never drop or rename them. A `{{tax}}` / `{tax}` filled with a tax name (VAT, GST, cukai keuntungan…) follows the noun it qualifies: "penyata {{tax}}", "{{tax}} input".
- Product names stay: Gnos3, K4mi, SmartOffice, Ollama, Open WebUI, Excel, PDF, CSV, MPF, ICMS, currency codes, units.

## Accounting and finance

| English | Malay (ms-MY) |
|---|---|
| account (ledger account, `Account_gnos3`) | akaun |
| account (user login) | akaun pengguna |
| account name / code | nama akaun / kod akaun |
| account type | jenis akaun |
| chart of accounts | carta akaun |
| control account (with sub-accounts) | akaun kawalan |
| sub-account | subakaun |
| detail / leaf account | akaun terperinci |
| journal entry / entry / transaction (books) | catatan jurnal / catatan |
| line (of an entry) | baris catatan |
| journal | jurnal |
| general ledger / ledger | lejar am / lejar |
| sub-ledger | sublejar |
| trial balance | imbangan duga |
| balance sheet | kunci kira-kira |
| profit and loss / income statement / P&L | penyata untung rugi (short: untung rugi) |
| statement of financial position (HK) | penyata kedudukan kewangan |
| statement of profit or loss (HK) | penyata untung atau rugi |
| assets / liabilities | aset / liabiliti |
| current / non-current assets | aset semasa / aset bukan semasa |
| current / non-current liabilities | liabiliti semasa / liabiliti bukan semasa |
| equity | ekuiti |
| revenue / income | hasil / pendapatan |
| cost of sales (COGS) | kos jualan |
| gross profit / net profit | untung kasar / untung bersih |
| retained earnings | pendapatan tertahan |
| opening balance | baki pembukaan |
| closing balance | baki penutup |
| debit / credit | debit / kredit |
| draft | draf |
| post (an entry) / posted | pos / telah dipos ("Pos", status "Dipos") |
| void / voided | batalkan catatan / dibatalkan ("Void" button = "Batalkan catatan", never just "Batal" = Cancel) |
| reversal (entry) | catatan songsangan |
| book (an invoice) / booking | rekod / perekodan |
| booking defaults | tetapan lalai perekodan |
| accounting period / period | tempoh perakaunan / tempoh |
| fiscal year / FY | tahun kewangan / TK |
| year to date (YTD) | tahun hingga kini |
| year-end closing | penutupan akhir tahun |
| close / reopen (a period) | tutup / buka semula |
| closing checklist | senarai semak penutupan |
| gap (line awaiting an account) | baris tertangguh |
| blocker | halangan |
| bank reconciliation | penyesuaian bank |
| match / unmatch / matched | padankan / nyahpadan / dipadankan |
| match group | kumpulan padanan |
| auto-match | padanan automatik |
| bank statement / bank line | penyata bank / baris bank |
| bank account | akaun bank |
| counterparty | pihak lawan |
| accounts payable / receivable (AP / AR) | akaun belum bayar / akaun belum terima |
| AP / AR aging | analisis umur akaun belum bayar / belum terima |
| supplier / vendor | pembekal |
| customer / client | pelanggan |
| payer / payee | pembayar / penerima bayaran |
| invoice / bill (supplier invoice) | invois / invois pembekal |
| receipt | resit |
| payment / payment in / payment out | pembayaran / penerimaan / pembayaran keluar |
| payment method | kaedah pembayaran |
| bank transfer / cheque / credit card / cash | pindahan bank / cek / kad kredit / tunai |
| currency / base currency | mata wang / mata wang asas |
| exchange rate | kadar pertukaran |
| exchange difference / gain / loss | perbezaan pertukaran / keuntungan pertukaran / kerugian pertukaran |
| exchange clearing account | akaun penjelasan pertukaran |
| categorization rule | peraturan pengkategorian |
| split (across accounts) | pecahan / pecahkan |
| fixed asset | aset tetap |
| depreciation / accumulated depreciation | susut nilai / susut nilai terkumpul |
| useful life / salvage value / book value | hayat berguna / nilai sisa / nilai buku |
| expense (account type, P&L) | perbelanjaan |
| expense sheet / expense claim (`Expenses_tab`) | tuntutan perbelanjaan |
| reimbursement | bayaran balik |
| employee | pekerja |
| approve / reject / submit | luluskan / tolak / hantar |
| company / legal entity name | syarikat / nama entiti sah |
| template | templat |
| VAT / GST / GST-HST / sales tax / consumption tax | VAT / GST / GST-HST / cukai jualan / cukai penggunaan |
| output / input VAT | VAT output / VAT input |
| VAT payable / VAT credit | VAT perlu dibayar / kredit VAT |
| brought forward / carried forward | dibawa dari tempoh lalu / dibawa ke tempoh hadapan |
| surcharge (China, on VAT) | surcaj |
| corporate income tax (CIT) | cukai pendapatan syarikat |
| individual income tax (IIT) | cukai pendapatan individu |
| profits tax (Hong Kong) | cukai keuntungan |
| provisional tax / prepaid tax | cukai sementara / cukai prabayar |
| assessment notice / demand note | notis taksiran / notis tuntutan |
| tax return / filing | penyata cukai / pemfailan |
| accrual entry | catatan akruan |
| settlement (of a tax) / settle | penyelesaian / selesaikan |
| tax computation adjustments / add-back / deduction | pelarasan cukai / tambahan semula / potongan |
| assessable profit | keuntungan boleh taksir |
| losses brought forward | kerugian dibawa ke hadapan |
| tax role mapping / mapped | pemetaan peranan cukai / dipetakan |

## Documents (K4mi) and modules

| English | Malay (ms-MY) |
|---|---|
| document | dokumen |
| tag | tag |
| custom field | medan tersuai |
| correspondent | pengirim |
| document type | jenis dokumen |
| storage path | laluan storan |
| owner | pemilik |
| title / content | tajuk / kandungan |
| note | nota |
| workflow | aliran kerja |
| saved view | paparan tersimpan |
| archive serial number (ASN) | nombor siri arkib (ASN) |
| inbox | peti masuk |
| business card | kad perniagaan |
| needs review / mark reviewed | perlu disemak / tandakan telah disemak |
| extraction | pengekstrakan |
| anonymise / Anonymiser | anonimkan / Penganonim |
| knowledge base | pangkalan pengetahuan |

## UI words

| English | Malay (ms-MY) |
|---|---|
| settings | tetapan |
| dashboard | papan pemuka |
| save / save changes | simpan / simpan perubahan |
| cancel | batal |
| delete | padam |
| edit | edit |
| create / new | cipta / baharu |
| add / remove | tambah / alih keluar |
| update | kemas kini |
| search | cari (noun: carian) |
| filter | penapis (verb: tapis) |
| sort | isih |
| export / import | eksport / import |
| upload / download | muat naik / muat turun |
| apply | guna |
| confirm | sahkan |
| close | tutup |
| back / next / previous | kembali / seterusnya / sebelumnya |
| retry | cuba semula |
| refresh | muat semula |
| loading… / saving… | memuatkan… / menyimpan… |
| error / warning | ralat / amaran |
| success / failed | berjaya / gagal |
| required / optional | wajib / pilihan |
| status | status |
| permissions / group / role | kebenaran / kumpulan / peranan |
| enable / disable | dayakan / nyahdayakan |
| file | fail |
| preview | pratonton |
| total / amount | jumlah / amaun |
| date / description / reference | tarikh / penerangan / rujukan |
| yes / no | ya / tidak |
