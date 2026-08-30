import type { IngestionRun, ProcessingStage } from './types';

export const processingStages: ProcessingStage[] = [
	{ name: 'Fetched', detail: '1,248 received' },
	{ name: 'Validated', detail: '1,248 accepted' },
	{ name: 'Normalized', detail: '1,248 normalized' },
	{ name: 'Ready', detail: 'Forecast ready' },
];

export const ingestionRuns: IngestionRun[] = [
	{ source: 'ERPNext sync', time: 'Today, 09:42', records: '1,248 records' },
	{
		source: 'ERPNext sync',
		time: 'Yesterday, 09:38',
		records: '1,244 records',
	},
	{
		source: 'April close upload',
		time: '28 Jun 2025',
		records: '4,806 records',
	},
];
