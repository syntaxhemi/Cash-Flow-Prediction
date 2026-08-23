/**
 * Converts a machine-readable status into a human-readable label.
 */
export function formatStatus(status: string | null | undefined): string {
	if (!status) {
		return '—';
	}

	return status
		.trim()
		.toLowerCase()
		.replace(/[-_]+/g, ' ')
		.replace(/\b\w/g, (character) => character.toUpperCase());
}
