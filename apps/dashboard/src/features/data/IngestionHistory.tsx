import { useState } from 'react';
import {
	LuCircleCheck,
	LuChevronLeft,
	LuChevronRight,
	LuClock3,
	LuDatabase,
	LuLayers3,
} from 'react-icons/lu';
import { cn } from '@/utils/cn';
import { ingestionRuns } from './mock-data';
import DataSectionEyebrow from './DataSectionEyebrow';

const paginationPages = ['1', '2', '3', '4'];

function HeaderIcon({ icon: Icon }: { icon: typeof LuDatabase }) {
	return (
		<Icon
			className="size-4 text-primary"
			strokeWidth={1.6}
			aria-hidden="true"
		/>
	);
}

function IngestionHistory() {
	const [currentPage, setCurrentPage] = useState('1');

	return (
		<section className="mt-14" aria-labelledby="history-title">
			<DataSectionEyebrow>Ingestion history</DataSectionEyebrow>
			<h2 id="history-title" className="sr-only">
				Ingestion run history
			</h2>
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
					{ingestionRuns.map((run) => (
						<div
							key={`${run.source}-${run.time}`}
							className="relative grid grid-cols-[minmax(0,1.15fr)_minmax(0,1fr)_minmax(0,1fr)_auto] items-center justify-items-start gap-2 border-b border-border/80 px-3 py-4 text-left text-xs last:border-b-0 max-[419px]:grid-cols-[minmax(0,1.15fr)_minmax(0,1fr)_minmax(0,1fr)_5.125rem] max-[419px]:px-2 sm:grid-cols-[minmax(0,1.15fr)_minmax(0,1fr)_minmax(0,1fr)_9rem] sm:gap-4 sm:px-5 sm:py-4 sm:text-sm"
						>
							<span
								className="absolute left-2 top-1/2 h-3 w-1 -translate-y-1/2 rounded-full bg-primary sm:left-3"
								aria-hidden="true"
							/>
							<span className="min-w-0 whitespace-normal break-words justify-self-start pl-3 text-ink max-[419px]:w-full max-[419px]:pl-2 max-[419px]:truncate sm:pl-4">
								{run.source}
							</span>
							<span className="min-w-0 whitespace-normal break-words justify-self-start tabular-nums text-text-muted max-[419px]:w-full max-[419px]:truncate">
								{run.time}
							</span>
							<span className="min-w-0 whitespace-normal break-words justify-self-start tabular-nums text-ink max-[419px]:w-full max-[419px]:truncate">
								{run.records}
							</span>
							<span className="inline-flex w-fit justify-self-start items-center gap-1 rounded-control bg-[#e6f0e9] px-1.5 py-1 text-[10px] font-medium text-positive sm:gap-1.5 sm:px-2.5 sm:text-[11px]">
								<LuCircleCheck
									className="size-3.5 sm:size-4"
									aria-hidden="true"
								/>
								Completed
							</span>
						</div>
					))}
				</div>
			</div>

			<nav
				className="mt-5 flex items-center justify-center gap-4 text-sm text-text-muted"
				aria-label="Ingestion history pagination"
			>
				<span className="tabular-nums">1–3 of 12</span>
				<button
					type="button"
					className="p-1 hover:text-primary"
					aria-label="Previous page"
				>
					<LuChevronLeft className="size-4" aria-hidden="true" />
				</button>
				{paginationPages.map((page) => (
					<button
						key={page}
						type="button"
						onClick={() => setCurrentPage(page)}
						aria-current={currentPage === page ? 'page' : undefined}
						className={cn(
							'relative min-w-5 p-1 text-center hover:text-primary',
							currentPage === page &&
								'font-medium text-primary after:absolute after:inset-x-0 after:-bottom-1 after:h-0.5 after:bg-primary',
						)}
					>
						{page}
					</button>
				))}
				<button
					type="button"
					className="p-1 hover:text-primary"
					aria-label="Next page"
				>
					<LuChevronRight className="size-4" aria-hidden="true" />
				</button>
			</nav>
		</section>
	);
}

export default IngestionHistory;
