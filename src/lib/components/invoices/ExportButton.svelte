<script lang="ts">
	import { getContext } from 'svelte';
	import { toast } from 'svelte-sonner';
	import dayjs from 'dayjs';

	import Download from '@lucide/svelte/icons/download';
	import ChevronDown from '@lucide/svelte/icons/chevron-down';
	import FileText from '@lucide/svelte/icons/file-text';
	import FileSpreadsheet from '@lucide/svelte/icons/file-spreadsheet';

	import { Button } from '$lib/components/ui/button/index.js';
	import * as DropdownMenu from '$lib/components/ui/dropdown-menu/index.js';

	const i18n: any = getContext('i18n');

	export let invoices: any[] = [];

	const EXPORT_COLUMNS = [
		'id',
		'vendor_name',
		'invoice_number',
		'invoice_date',
		'due_date',
		'currency',
		'subtotal',
		'tax_amount',
		'total_amount',
		// amount_paid / balance_due deliberately absent — accounting state, not
		// extracted invoice data; exporting them from here published wrong figures.
		'payment_terms',
		'po_number',
		'description',
		'processing_status',
		'confidence_score',
		'k4mi_document_id'
	];

	const exportCsv = () => {
		if (!invoices.length) {
			toast.error($i18n.t('No data to export'));
			return;
		}

		const header = EXPORT_COLUMNS.join(',');
		const rows = invoices.map((inv) =>
			EXPORT_COLUMNS.map((col) => {
				const val = inv[col];
				if (val === null || val === undefined) return '';
				const str = String(val);
				if (str.includes(',') || str.includes('"') || str.includes('\n')) {
					return `"${str.replace(/"/g, '""')}"`;
				}
				return str;
			}).join(',')
		);

		const csv = [header, ...rows].join('\n');
		downloadFile(csv, `invoices-export-${dayjs().format('YYYY-MM-DD')}.csv`, 'text/csv');
		toast.success($i18n.t('Exported CSV'));
	};

	const exportXlsx = async () => {
		if (!invoices.length) {
			toast.error($i18n.t('No data to export'));
			return;
		}

		try {
			const XLSX = await import('xlsx');
			const wsData = [
				EXPORT_COLUMNS,
				...invoices.map((inv) => EXPORT_COLUMNS.map((col) => inv[col] ?? ''))
			];
			const ws = XLSX.utils.aoa_to_sheet(wsData);
			const wb = XLSX.utils.book_new();
			XLSX.utils.book_append_sheet(wb, ws, 'Invoices');
			XLSX.writeFile(wb, `invoices-export-${dayjs().format('YYYY-MM-DD')}.xlsx`);
			toast.success($i18n.t('Exported Excel'));
		} catch (err) {
			toast.error(`Export failed: ${err}`);
		}
	};

	const downloadFile = (content: string, filename: string, type: string) => {
		const blob = new Blob([content], { type });
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = filename;
		a.click();
		URL.revokeObjectURL(url);
	};
</script>

<DropdownMenu.Root>
	<DropdownMenu.Trigger>
		{#snippet child({ props })}
			<Button {...props} variant="outline" size="sm">
				<Download />{$i18n.t('Export')}<ChevronDown class="text-muted-foreground" />
			</Button>
		{/snippet}
	</DropdownMenu.Trigger>
	<DropdownMenu.Content align="end" class="w-44">
		<DropdownMenu.Item onSelect={exportCsv}><FileText />CSV</DropdownMenu.Item>
		<DropdownMenu.Item onSelect={exportXlsx}><FileSpreadsheet />Excel (XLSX)</DropdownMenu.Item>
	</DropdownMenu.Content>
</DropdownMenu.Root>
