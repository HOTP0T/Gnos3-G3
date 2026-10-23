// Taxes are named in the UI language, never in the company country's: a French
// company's VAT reads "VAT" in English, "TVA" in French, "增值税" in Chinese. The
// country config says what each tax is (`tax_kind`, `cit_kind`); these are the
// i18n keys for it. The country's own labels (TVA collectée, 企业所得税…) stay
// in Settings → Countries as reference data and are not shown on screens.

export const TAX_KIND_TERMS: Record<string, string> = {
	vat: 'VAT',
	gst: 'GST',
	gst_hst: 'GST/HST',
	consumption: 'Consumption tax',
	icms: 'ICMS',
	sales: 'Sales tax'
};

export const CIT_KIND_TERMS: Record<string, string> = {
	cit: 'Corporate income tax',
	profits_tax: 'Profits Tax'
};

type Translate = (key: string, options?: Record<string, unknown>) => string;

/** The country's indirect tax (VAT, GST…) in the UI language. */
export const taxTerm = (t: Translate, cfg: { tax_kind?: string } | null | undefined): string =>
	t(TAX_KIND_TERMS[cfg?.tax_kind ?? ''] ?? 'VAT');

/** The country's company income tax (corporate income tax, Profits Tax) in the UI language. */
export const citTerm = (t: Translate, cfg: { cit_kind?: string } | null | undefined): string =>
	t(CIT_KIND_TERMS[cfg?.cit_kind ?? ''] ?? 'Corporate income tax');
