import {
	LuCheck,
	LuDatabase,
	LuPause,
	LuPencil,
	LuRefreshCw,
} from 'react-icons/lu';
import type {
	IngestionRun,
	IngestionSource,
	IngestionSourceCredential,
} from '@/api/contracts';
import Button from '@/components/ui/Button';
import { cn } from '@/utils/cn';
import DataIconBox from './DataIconBox';
import DataSectionEyebrow from './DataSectionEyebrow';

type DataSourcePanelProps = {
	selectedSource: IngestionSource | null;
	latestRun: IngestionRun | null;
	credential: IngestionSourceCredential | null;
	syncing: boolean;
	onSync: () => void;
	onEdit: () => void;
	onDeactivate: () => void;
};

function sourceLabel(source: IngestionSource) {
	if (source.source_key === 'erpnext') return 'ERPNext';
	if (source.source_key === 'excel') return 'XLSX import';
	return source.display_name;
}

function formatFreshness(value: string | null | undefined) {
	if (!value) return 'Not synced yet';
	return `Last synced ${new Date(value).toLocaleString('en-IN', {
		dateStyle: 'medium',
		timeStyle: 'short',
	})}`;
}

function formatNumber(value: number) {
	return new Intl.NumberFormat('en-IN').format(value);
}

function DataSourcePanel({
	selectedSource,
	latestRun,
	credential,
	syncing,
	onSync,
	onEdit,
	onDeactivate,
}: DataSourcePanelProps) {
	if (!selectedSource) {
		return (
			<article className="rounded-card border border-primary/20 bg-surface p-5 sm:p-6">
				<DataSectionEyebrow>Connected sources</DataSectionEyebrow>
				<h2 className="mt-4 font-serif text-2xl text-ink">
					No data source connected
				</h2>
				<p className="mt-2 text-sm leading-relaxed text-text-muted">
					Connect an accounting source or add a file source to start processing
					financial data.
				</p>
			</article>
		);
	}

	return (
		<article className="rounded-card border border-primary/20 bg-surface p-5 sm:p-6">
			<DataSectionEyebrow>Connected source</DataSectionEyebrow>
			<div className="mt-6 grid gap-6 xl:grid-cols-[minmax(0,1fr)_9.5rem] xl:gap-7">
				<div className="flex min-w-0 items-start gap-4">
					<DataIconBox icon={LuDatabase} />
					<div className="min-w-0">
						<div className="flex flex-nowrap items-baseline gap-x-2 sm:gap-x-3">
							<h2 className="whitespace-nowrap font-serif text-xl leading-none text-ink sm:text-4xl">
								{sourceLabel(selectedSource)}
							</h2>
							<span
								className={cn(
									'inline-flex shrink-0 items-center gap-1.5 rounded-control px-2.5 py-1 text-xs font-medium',
									selectedSource.status === 'active'
										? 'bg-[#e6f0e9] text-positive'
										: selectedSource.status === 'error'
											? 'bg-risk/10 text-risk'
											: 'bg-primary-soft text-primary',
								)}
							>
								<LuCheck className="size-3.5" aria-hidden="true" />
								{selectedSource.status === 'active'
									? 'Connected'
									: selectedSource.status === 'error'
										? 'Needs attention'
										: 'Paused'}
							</span>
						</div>
						<p className="mt-3 text-xs text-text-muted sm:text-base">
							{selectedSource.display_name}
							<span className="mx-2" aria-hidden="true">
								•
							</span>
							{credential ? 'Credentials configured' : 'No credentials configured'}
						</p>
						<p className="mt-2 text-xs text-text-muted sm:text-sm">
							{formatFreshness(selectedSource.last_synced_at)}
						</p>
					</div>
				</div>

				<div className="flex items-baseline gap-2 border-t border-border/80 pt-5 xl:block xl:border-l xl:border-t-0 xl:pl-7 xl:pt-0">
					<p className="font-serif text-3xl leading-none tabular-nums text-ink sm:text-5xl">
						{formatNumber(latestRun?.records_processed ?? 0)}
					</p>
					<p className="text-sm text-text-muted xl:mt-2">normalized records</p>
				</div>
			</div>

			<div className="mt-7 flex items-center justify-between gap-3">
				<Button
					className="shrink-0"
					size="md"
					leading={
						<LuRefreshCw className={cn('size-4', syncing && 'animate-spin')} />
					}
					onClick={onSync}
					disabled={syncing || selectedSource.status !== 'active'}
				>
					{syncing ? 'Syncing...' : 'Sync now'}
				</Button>
				<div className="ml-auto flex items-center gap-5 sm:gap-6">
					<button
						type="button"
						className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
						aria-label="Edit source"
						onClick={onEdit}
					>
						<LuPencil className="size-4" aria-hidden="true" />
						<span className="hidden sm:inline">Edit source</span>
					</button>
					<button
						type="button"
						className="inline-flex items-center gap-2 text-sm text-text-muted hover:text-primary"
						aria-label="Deactivate source"
						onClick={onDeactivate}
					>
						<LuPause className="size-4" aria-hidden="true" />
						<span className="hidden sm:inline">Deactivate source</span>
					</button>
				</div>
			</div>
		</article>
	);
}

export default DataSourcePanel;
