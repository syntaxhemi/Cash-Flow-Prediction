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
		maximumFractionDigits = 1,
		minimumFractionDigits = 0,
	}: CurrencyFormatOptions = {},
): string {
	if (value === null || value === undefined || !Number.isFinite(value)) {
		return '—';
	}

	const absolute = Math.abs(value);
	const units = [
		{ threshold: 1_000_000_000, suffix: 'B' },
		{ threshold: 1_000_000, suffix: 'M' },
		{ threshold: 1_000, suffix: 'K' },
	];
	const unit = units.find(({ threshold }) => absolute >= threshold);
	const scaledValue = unit ? absolute / unit.threshold : absolute;
	const number = new Intl.NumberFormat(locale, {
		maximumFractionDigits,
		minimumFractionDigits,
	}).format(scaledValue);
	const symbol = new Intl.NumberFormat(locale, {
		style: 'currency',
		currency,
		currencyDisplay: 'narrowSymbol',
		maximumFractionDigits: 0,
	})
		.formatToParts(0)
		.find((part) => part.type === 'currency')?.value;

	return `${value < 0 ? '-' : ''}${symbol ?? currency}${number}${unit?.suffix ?? ''}`;
}
