import { useState } from 'react';
import {
	LuCheck,
	LuDatabase,
	LuPause,
	LuPencil,
	LuRefreshCw,
} from 'react-icons/lu';
import Button from '@/components/ui/Button';
import { cn } from '@/utils/cn';
import DataIconBox from './DataIconBox';
import DataSectionEyebrow from './DataSectionEyebrow';

function DataSourcePanel() {
	const [syncing, setSyncing] = useState(false);

	function handleSync() {
		setSyncing(true);
		window.setTimeout(() => setSyncing(false), 900);
	}

	return (
		<article className="rounded-card border border-primary/20 bg-surface p-5 sm:p-6">
			<DataSectionEyebrow>Connected source</DataSectionEyebrow>
			<div className="mt-6 grid gap-6 xl:grid-cols-[minmax(0,1fr)_9.5rem] xl:gap-7">
				<div className="flex min-w-0 items-start gap-4">
					<DataIconBox icon={LuDatabase} />
					<div className="min-w-0">
						<div className="flex flex-nowrap items-center gap-x-2 sm:gap-x-3">
							<h2 className="whitespace-nowrap font-serif text-xl leading-none text-ink sm:text-4xl">
								ERPNext
							</h2>
							<span className="inline-flex shrink-0 items-center gap-1.5 rounded-control bg-[#e6f0e9] px-2.5 py-1 text-xs font-medium text-positive">
								<LuCheck className="size-3.5" aria-hidden="true" />
								Connected
							</span>
						</div>
						<p className="mt-3 text-xs text-text-muted sm:text-base">
							Northstar Manufacturing
							<span className="mx-2" aria-hidden="true">
								•
							</span>
							Production ledger
						</p>
						<p className="mt-2 text-xs text-text-muted sm:text-sm">
							Synced 8 min ago
						</p>
					</div>
				</div>

				<div className="border-t border-border/80 pt-5 xl:border-l xl:border-t-0 xl:pl-7 xl:pt-0">
					<p className="font-serif text-3xl leading-none tabular-nums text-ink sm:text-5xl">
						1,248
					</p>
					<p className="mt-2 text-sm text-text-muted">normalized records</p>
				</div>
			</div>

			<div className="mt-7 flex items-center justify-between gap-3">
				<Button
					className="shrink-0"
					size="md"
					leading={
						<LuRefreshCw className={cn('size-4', syncing && 'animate-spin')} />
					}
					onClick={handleSync}
				>
					{syncing ? 'Syncing...' : 'Sync now'}
				</Button>
				<div className="ml-auto flex items-center gap-5 sm:gap-6">
					<button
						type="button"
						className="inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
						aria-label="Edit source"
					>
						<LuPencil className="size-4" aria-hidden="true" />
						<span className="hidden sm:inline">Edit source</span>
					</button>
					<button
						type="button"
						className="inline-flex items-center gap-2 text-sm text-text-muted hover:text-primary"
						aria-label="Deactivate source"
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
