type CurrencyFormatOptions = {
	currency?: string;
	locale?: string;
	maximumFractionDigits?: number;
	minimumFractionDigits?: number;
};

/**
 * Formats a numeric value as a currency amount.
 */
export function formatCurrency(
	value: number | null | undefined,
	{
		currency = 'INR',
		locale = 'en-IN',
		maximumFractionDigits = 0,
		minimumFractionDigits = 0,
	}: CurrencyFormatOptions = {},
): string {
	if (value === null || value === undefined || Number.isNaN(value)) {
		return '—';
	}

	return new Intl.NumberFormat(locale, {
		style: 'currency',
		currency,
		maximumFractionDigits,
		minimumFractionDigits,
	}).format(value);
}
