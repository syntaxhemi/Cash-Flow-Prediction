import type { ReceivablePriority } from './types';

export const priorityStyles: Record<ReceivablePriority, string> = {
	Critical: 'bg-primary-soft text-primary',
	High: 'bg-[#f7eee6] text-warning',
	Watch: 'bg-canvas text-ink',
	Stable: 'bg-[#e9f0eb] text-positive',
};
