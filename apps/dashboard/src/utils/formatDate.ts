type DateFormatOptions = Intl.DateTimeFormatOptions & {
	locale?: string;
};

/**
 * Formats a date-like value for dashboard display.
 */
export function formatDate(
	value: string | number | Date | null | undefined,
	{ locale = 'en-US', ...options }: DateFormatOptions = {},
): string {
	if (value === null || value === undefined) {
		return '—';
	}

	const date = value instanceof Date ? value : new Date(value);

	if (Number.isNaN(date.getTime())) {
		return '—';
	}

	return new Intl.DateTimeFormat(locale, {
		day: 'numeric',
		month: 'short',
		year: 'numeric',
		...options,
	}).format(date);
}
