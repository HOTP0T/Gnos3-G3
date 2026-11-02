# Gnos3 business modules — Indonesian (id-ID) glossary

## Conventions

- **Form of address: "Anda"** (always capitalised), formal register; never "kamu" / "-mu". Prefer impersonal or passive phrasing where it reads naturally ("Perusahaan belum dibuat", "Tindakan ini tidak dapat dibatalkan").
- **Buttons and menu actions: bare imperative verb** (no *me-* prefix), object after the verb: "Simpan", "Hapus", "Buat entri", "Unggah berkas", "Terapkan filter". Do not use "Menghapus" / "Menyimpan" on buttons. Progress states use *me-* + "…": "Memuat…", "Menyimpan…", "Mengunggah…". Titles and labels are noun phrases ("Entri baru", "Pengaturan perusahaan").
- **Sentence case**: capital only on the first word, proper names, month and day names (Indonesian capitalises them: Januari, Senin) and "Anda". ALL-CAPS statement totals stay in capitals.
- **Punctuation**: no space before ":" "?" "!" ";". Quoted UI labels and names in “…”. Ellipsis "…" for progress. "e.g." → "mis." (misalnya), "i.e." → "yaitu", "etc." → "dll.", "vs." → "vs.".
- **Numbers and dates**: decimal comma, thousands point (1.234,56); dates dd/mm/yyyy (30/10/2026); "s.d." (sampai dengan) for ranges and "through" ("Jan s.d. Mar"); percent without a space (11%). Currency codes before the amount (IDR 1.000.000, EUR 12,50).
- **Plurals**: Indonesian does not inflect; do not reduplicate nouns ("dokumen-dokumen") unless needed for meaning — "{{count}} dokumen", "3 faktur". Singular and plural English keys usually get the same Indonesian text.
- **Loanwords** are written the Indonesian way: draf, templat, akun, entri, posting, rekonsiliasi, kategori, dasbor, berkas (file), unggah / unduh, ekspor / impor.
- **DR / CR** → **D / K** in column headers; "Debit" / "Kredit" written out elsewhere.
- **Placeholders** ({{name}}, {name}, <0>, <1/>) stay exactly as given; word order may move them, never drop or rename them. A `{{tax}}` / `{tax}` filled with a tax name (PPN, GST, PPh Badan…) is used without an article: "SPT {{tax}}", "{{tax}} masukan".
- Product names stay: Gnos3, K4mi, SmartOffice, Ollama, Open WebUI, Excel, PDF, CSV, MPF, ICMS, currency codes, units.

## Accounting and finance

| English | Indonesian (id-ID) |
|---|---|
| account (ledger account, `Account_gnos3`) | akun |
| account (user login) | akun pengguna |
| account name / code | nama akun / kode akun |
| account type | jenis akun |
| chart of accounts | bagan akun |
| control account (with sub-accounts) | akun kontrol (akun induk) |
| sub-account | subakun |
| detail / leaf account | akun detail |
| journal entry / entry / transaction (books) | entri jurnal / entri |
| line (of an entry) | baris entri |
| journal | jurnal |
| general ledger / ledger | buku besar |
| sub-ledger | buku besar pembantu |
| trial balance | neraca saldo |
| balance sheet | neraca |
| profit and loss / income statement / P&L | laporan laba rugi (short: laba rugi) |
| statement of financial position (HK) | laporan posisi keuangan |
| statement of profit or loss (HK) | laporan laba rugi |
| assets / liabilities | aset / liabilitas |
| current / non-current assets | aset lancar / aset tidak lancar |
| current / non-current liabilities | liabilitas jangka pendek / liabilitas jangka panjang |
| equity | ekuitas |
| retained earnings | laba ditahan |
| revenue / income | pendapatan |
| expense (account type, P&L, dashboards) | beban |
| cost of sales / COGS | harga pokok penjualan (HPP) |
| gross profit / operating profit / net income | laba kotor / laba usaha / laba bersih |
| opening balance (entries: opening entry) | saldo awal (entri saldo awal) |
| closing balance | saldo akhir |
| debit / credit | debit / kredit (columns: D / K) |
| draft | draf |
| post / posted | posting / diposting |
| book (an invoice), booking | bukukan, pembukuan |
| booking defaults | pengaturan default pembukuan |
| booking engine | mesin pembukuan |
| void / voided | batalkan / dibatalkan (button "Void" = "Batalkan entri", never just "Batal" = Cancel) |
| reversal (entry) | jurnal pembalik |
| accounting period / period | periode akuntansi / periode |
| fiscal year / FY | tahun buku / TB |
| year-end closing | tutup buku akhir tahun |
| year to date (YTD) | tahun berjalan (column: s.d. tahun berjalan) |
| close / reopen a period | tutup / buka kembali |
| closing checklist | daftar periksa tutup buku |
| blocker | kendala (blocking issue) |
| gap (line awaiting an account) | baris tertunda (belum ada akun) |
| bank reconciliation | rekonsiliasi bank |
| match / unmatch / matched | cocokkan / batalkan pencocokan / dicocokkan |
| auto-match | pencocokan otomatis |
| match group | grup pencocokan |
| bank statement | rekening koran |
| bank line (one line of a statement) | mutasi bank |
| counterparty | pihak lawan |
| accounts payable / receivable (AP / AR) | utang usaha / piutang usaha |
| AP / AR aging | umur utang / umur piutang |
| aging bucket / "Current" bucket | rentang umur / belum jatuh tempo |
| supplier / vendor | pemasok |
| customer / client | pelanggan |
| invoice / bill (supplier invoice) | faktur / faktur pemasok |
| sales invoice | faktur penjualan |
| receipt (expense proof) | bukti pengeluaran (struk / kuitansi) |
| payment / payment in / payment out | pembayaran / penerimaan / pengeluaran |
| payer / payee | pembayar / penerima pembayaran |
| payment method | metode pembayaran |
| bank transfer / check / credit card / cash | transfer bank / cek / kartu kredit / tunai |
| currency / base currency | mata uang / mata uang dasar |
| exchange rate | kurs |
| exchange difference / gain / loss | selisih kurs / laba selisih kurs / rugi selisih kurs |
| exchange clearing account | akun kliring valas |
| rate override (company rate) | kurs khusus |
| categorization rule | aturan kategorisasi |
| bank-line rule | aturan mutasi bank |
| pattern | pola |
| split (across accounts) | pecah, pemecahan |
| fixed asset | aset tetap |
| depreciation / accumulated depreciation | penyusutan / akumulasi penyusutan |
| useful life / salvage value / book value | masa manfaat / nilai residu / nilai buku |
| straight-line / declining balance | garis lurus / saldo menurun |
| asset register | daftar aset tetap |
| expense sheet / expense claim | lembar pengeluaran / klaim pengeluaran |
| expenses (the expense-claims tab, `Expenses_tab`) | klaim pengeluaran |
| reimbursement | penggantian biaya |
| employee | karyawan |
| approve / reject / submit | setujui / tolak / ajukan |
| company | perusahaan |
| legal entity name | nama badan hukum |
| template | templat |

## Taxes

| English | Indonesian (id-ID) |
|---|---|
| tax (generic) / `Tax_tab` | pajak / Pajak |
| VAT | PPN (Pajak Pertambahan Nilai) |
| GST / GST-HST / sales tax / consumption tax | GST / GST/HST / pajak penjualan / pajak konsumsi |
| output / input VAT | PPN keluaran / PPN masukan |
| VAT payable / VAT credit | PPN kurang bayar / PPN lebih bayar |
| VAT return | SPT Masa PPN (short: SPT PPN) |
| credit brought forward / carried forward | lebih bayar dari periode lalu / lebih bayar dikompensasikan ke periode berikutnya |
| surcharge (China, on VAT) | pajak tambahan |
| corporate income tax (CIT) | PPh Badan (Pajak Penghasilan Badan) |
| individual income tax (IIT) | PPh Orang Pribadi |
| profits tax (Hong Kong) | pajak laba (Profits Tax) |
| provisional tax | pajak sementara (angsuran pajak) |
| prepaid tax | pajak dibayar di muka |
| assessment notice / demand note | surat ketetapan pajak / surat tagihan pajak |
| tax return / filing / declaration | SPT / pelaporan pajak |
| accrual entry (tax) | entri akrual pajak |
| settlement entry (VAT) | entri penyelesaian |
| settle (a filing) | selesaikan / lunasi |
| add-back / deduction | koreksi positif / koreksi negatif |
| tax computation adjustments | koreksi fiskal |
| adjusted / assessable profit | laba fiskal / penghasilan kena pajak |
| losses brought forward | kompensasi kerugian |
| two-tier / tiered rates | tarif dua lapis / tarif berjenjang |
| tax role mapping / mapped | pemetaan / dipetakan |
| withholding | pemotongan pajak |
| due date | jatuh tempo |

## Documents (K4mi)

| English | Indonesian (id-ID) |
|---|---|
| document | dokumen |
| tag (K4mi document tag) | label (label K4mi) |
| tag (chat / Open WebUI tag) | tag |
| custom field | bidang khusus |
| correspondent | koresponden |
| document type | jenis dokumen |
| storage path | lokasi penyimpanan |
| workflow | alur kerja |
| owner | pemilik |
| business card | kartu nama |
| needs review / mark reviewed | perlu ditinjau / tandai sudah ditinjau |
| extraction / extract | ekstraksi / ekstrak |
| reprocess | proses ulang |
| preview | pratinjau |
| file | berkas |

## UI words

| English | Indonesian (id-ID) |
|---|---|
| settings | pengaturan |
| dashboard | dasbor |
| save | simpan |
| cancel | batal |
| delete / remove | hapus |
| edit | edit |
| create / add | buat / tambah |
| search | cari |
| filter | filter (verb: saring) |
| export / import | ekspor / impor |
| upload / download | unggah / unduh |
| apply | terapkan |
| confirm | konfirmasi |
| loading / saving | memuat… / menyimpan… |
| error / warning | kesalahan / peringatan |
| refresh | muat ulang |
| close | tutup |
| back / next / previous | kembali / berikutnya / sebelumnya |
| select / clear (filters) | pilih / bersihkan |
| permissions | izin akses |
| group / user | grup / pengguna |
| admin / superadmin | admin / superadmin |
| status | status |
| no results | tidak ada hasil |
| optional / required | opsional / wajib |
| enabled / disabled | aktif / nonaktif |
