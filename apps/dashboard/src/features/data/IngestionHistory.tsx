import { useState } from 'react';
import {
	LuCircleAlert,
	LuCircleCheck,
	LuChevronLeft,
	LuChevronRight,
	LuClock3,
	LuDatabase,
	LuLayers3,
	LuRefreshCw,
} from 'react-icons/lu';
import type { IngestionRun, IngestionSource } from '@/api/contracts';
import Button from '@/components/ui/Button';
import { cn } from '@/utils/cn';
import DataSectionEyebrow from './DataSectionEyebrow';

type IngestionHistoryProps = {
	runs: IngestionRun[];
	sources: IngestionSource[];
	totalCount: number;
	page: number;
	pageSize: number;
	onPageChange: (page: number) => void;
	onRefresh: () => Promise<void>;
	refreshing: boolean;
};

function formatRunTime(value: string) {
	return new Date(value).toLocaleString('en-IN', {
		dateStyle: 'medium',
		timeStyle: 'short',
	});
}

function formatRunType(value: IngestionRun['run_type']) {
	if (value === 'upload') return 'File upload';
	if (value === 'full') return 'Full sync';
	return 'Incremental sync';
}

function HeaderIcon({ icon: Icon }: { icon: typeof LuDatabase }) {
	return (
		<Icon
			className="size-4 text-primary"
			strokeWidth={1.6}
			aria-hidden="true"
		/>
	);
}

function IngestionHistory({
	runs,
	sources,
	totalCount,
	page,
	pageSize,
	onPageChange,
	onRefresh,
	refreshing,
}: IngestionHistoryProps) {
	const [manualRefreshing, setManualRefreshing] = useState(false);
	const sourceNames = new Map(
		sources.map((source) => [source.id, source.display_name]),
	);
	const pageCount = Math.max(1, Math.ceil(totalCount / pageSize));
	const firstItem = totalCount === 0 ? 0 : page * pageSize + 1;
	const lastItem = Math.min((page + 1) * pageSize, totalCount);
	const isRefreshing = refreshing || manualRefreshing;

	const handleRefresh = async () => {
		setManualRefreshing(true);
		try {
			await Promise.all([
				onRefresh(),
				new Promise((resolve) => window.setTimeout(resolve, 600)),
			]);
		} finally {
			setManualRefreshing(false);
		}
	};

	return (
		<section className="mt-14" aria-labelledby="history-title">
			<div className="flex items-center justify-between gap-4">
				<DataSectionEyebrow>Ingestion run history</DataSectionEyebrow>
				<Button
					variant="ghost"
					size="sm"
					onClick={() => void handleRefresh()}
					disabled={isRefreshing}
					leading={
						<LuRefreshCw
							className={cn('size-4', isRefreshing && 'animate-spin')}
							aria-hidden="true"
						/>
					}
				>
					Refresh
				</Button>
			</div>
			<h2 id="history-title" className="sr-only">
				Ingestion run history
			</h2>
			{runs.length === 0 ? (
				<p className="mt-5 text-sm text-text-muted">
					No ingestion runs are available yet.
				</p>
			) : (
				<div className="mt-4 overflow-hidden rounded-control border border-border bg-surface max-[419px]:-mx-2">
					<div className="grid grid-cols-[minmax(0,1.15fr)_minmax(0,1fr)_minmax(0,1fr)_auto] items-center justify-items-start gap-2 border-b border-border px-3 py-3 text-left text-[10px] font-semibold uppercase tracking-[0.12em] text-text-muted max-[419px]:grid-cols-[minmax(0,1.15fr)_minmax(0,1fr)_minmax(0,1fr)_5.125rem] max-[419px]:px-2 sm:grid-cols-[minmax(0,1.15fr)_minmax(0,1fr)_minmax(0,1fr)_9rem] sm:gap-4 sm:px-5 sm:text-[11px] sm:tracking-[0.16em]">
						<span className="inline-flex min-w-0 justify-self-start items-center gap-1.5 sm:gap-2 max-[419px]:w-full max-[419px]:overflow-hidden">
							<HeaderIcon icon={LuDatabase} />
							<span className="whitespace-normal break-words max-[419px]:truncate">
								Source
							</span>
						</span>
						<span className="inline-flex min-w-0 justify-self-start items-center gap-1.5 sm:gap-2 max-[419px]:w-full max-[419px]:overflow-hidden">
							<HeaderIcon icon={LuClock3} />
							<span className="whitespace-normal break-words max-[419px]:truncate">
								Run time
							</span>
						</span>
						<span className="inline-flex min-w-0 justify-self-start items-center gap-1.5 sm:gap-2 max-[419px]:w-full max-[419px]:overflow-hidden">
							<HeaderIcon icon={LuLayers3} />
							<span className="whitespace-normal break-words max-[419px]:truncate">
								Records
							</span>
						</span>
						<span className="inline-flex justify-self-start items-center gap-1.5 sm:gap-2 max-[419px]:w-full max-[419px]:overflow-hidden">
							<HeaderIcon icon={LuCircleCheck} />
							<span>Status</span>
						</span>
					</div>
					<div>
						{runs.map((run) => {
							const failed = run.status === 'failed';
							return (
								<div
									key={run.id}
									className="relative grid grid-cols-[minmax(0,1.15fr)_minmax(0,1fr)_minmax(0,1fr)_auto] items-center justify-items-start gap-2 border-b border-border/80 px-3 py-4 text-left text-xs last:border-b-0 max-[419px]:grid-cols-[minmax(0,1.15fr)_minmax(0,1fr)_minmax(0,1fr)_5.125rem] max-[419px]:px-2 sm:grid-cols-[minmax(0,1.15fr)_minmax(0,1fr)_minmax(0,1fr)_9rem] sm:gap-4 sm:px-5 sm:py-4 sm:text-sm"
								>
									<span
										className={cn(
											'absolute left-2 top-1/2 h-3 w-1 -translate-y-1/2 rounded-full sm:left-3',
											failed ? 'bg-risk' : 'bg-primary',
										)}
										aria-hidden="true"
									/>
									<span className="min-w-0 whitespace-normal break-words justify-self-start pl-3 text-ink max-[419px]:w-full max-[419px]:pl-2 max-[419px]:truncate sm:pl-4">
										{sourceNames.get(run.ingestion_source_id) ?? 'Unknown source'} ·{' '}
										{formatRunType(run.run_type)}
									</span>
									<span className="min-w-0 whitespace-normal break-words justify-self-start tabular-nums text-text-muted max-[419px]:w-full max-[419px]:truncate">
										{formatRunTime(run.created_at)}
									</span>
									<span className="min-w-0 whitespace-normal break-words justify-self-start tabular-nums text-ink max-[419px]:w-full max-[419px]:truncate">
										{run.records_processed.toLocaleString('en-IN')} /{' '}
										{run.records_received.toLocaleString('en-IN')}
									</span>
									<span
										className={cn(
											'inline-flex w-fit justify-self-start items-center gap-1 rounded-control px-1.5 py-1 text-[10px] font-medium sm:gap-1.5 sm:px-2.5 sm:text-[11px]',
											failed
											? 'bg-risk/10 text-risk'
												: run.status === 'completed'
													? 'bg-[#e6f0e9] text-positive'
													: 'bg-primary-soft text-primary',
										)}
									>
										{failed ? (
												<LuCircleAlert className="size-3.5 sm:size-4" aria-hidden="true" />
											) : (
												<LuCircleCheck className="size-3.5 sm:size-4" aria-hidden="true" />
										)}
										{run.status === 'completed'
											? 'Completed'
											: run.status === 'failed'
												? 'Failed'
												: run.status === 'running'
													? 'Running'
													: 'Pending'}
									</span>
								</div>
							);
						})}
					</div>
				</div>
			)}

			{totalCount > 0 ? (
				<nav
					className="mt-5 flex items-center justify-center gap-4 text-sm text-text-muted"
					aria-label="Ingestion history pagination"
				>
					<span className="tabular-nums">
						{firstItem}–{lastItem} of {totalCount}
					</span>
					<button
						type="button"
						className="p-1 hover:text-primary disabled:opacity-40"
						disabled={page === 0}
						onClick={() => onPageChange(page - 1)}
						aria-label="Previous page"
					>
						<LuChevronLeft className="size-4" aria-hidden="true" />
					</button>
					{Array.from({ length: Math.min(pageCount, 5) }, (_, index) => (
						<button
							key={index}
							type="button"
							onClick={() => onPageChange(index)}
							aria-current={page === index ? 'page' : undefined}
							className={cn(
								'relative min-w-5 p-1 text-center hover:text-primary',
								page === index &&
									'font-medium text-primary after:absolute after:inset-x-0 after:-bottom-1 after:h-0.5 after:bg-primary',
							)}
						>
							{index + 1}
						</button>
					))}
					<button
						type="button"
						className="p-1 hover:text-primary disabled:opacity-40"
						disabled={page >= pageCount - 1}
						onClick={() => onPageChange(page + 1)}
						aria-label="Next page"
					>
						<LuChevronRight className="size-4" aria-hidden="true" />
					</button>
				</nav>
			) : null}
		</section>
	);
}

export default IngestionHistory;
