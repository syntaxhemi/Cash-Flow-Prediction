import { LuCheck, LuCircleAlert, LuLoaderCircle, LuMoveRight } from 'react-icons/lu';
import type { IngestionRun } from '@/api/contracts';
import DataSectionEyebrow from './DataSectionEyebrow';

type ProcessingStatusProps = { run: IngestionRun | null };

type ProcessingStage = { name: string; detail: string; complete: boolean };

function ProcessingStatus({ run }: ProcessingStatusProps) {
	if (!run) {
		return (
			<section className="mt-14" aria-labelledby="processing-title">
				<DataSectionEyebrow>Latest processing</DataSectionEyebrow>
				<p id="processing-title" className="mt-5 text-sm text-text-muted">
					No processing run has been started yet.
				</p>
			</section>
		);
	}

	const stages: ProcessingStage[] = [
		{
			name: 'Received',
			detail: `${run.records_received.toLocaleString('en-IN')} records received`,
			complete: run.records_received > 0,
		},
		{
			name: 'Validated',
			detail:
				run.records_failed > 0
					? `${run.records_failed.toLocaleString('en-IN')} records need attention`
					: 'No validation errors reported',
			complete: run.status === 'completed' || run.status === 'running',
		},
		{
			name: 'Normalized',
			detail: `${run.records_processed.toLocaleString('en-IN')} records normalized`,
			complete: run.records_processed > 0,
		},
		{
			name: run.status === 'failed' ? 'Needs attention' : 'Ready',
			detail:
				run.status === 'failed'
					? run.error_summary ?? 'Processing failed'
					: run.status === 'completed'
						? 'Forecast data ready'
						: 'Processing in progress',
			complete: run.status === 'completed',
		},
	];

	function StageIcon({ stage }: { stage: ProcessingStage }) {
		if (run.status === 'failed' && stage.name === 'Needs attention') {
			return <LuCircleAlert className="size-5" aria-hidden="true" />;
		}
		if (run.status === 'running' && !stage.complete) {
			return <LuLoaderCircle className="size-5 animate-spin" aria-hidden="true" />;
		}
		return <LuCheck className="size-5" strokeWidth={2} aria-hidden="true" />;
	}

	return (
		<section className="mt-14" aria-labelledby="processing-title">
			<DataSectionEyebrow>Latest processing</DataSectionEyebrow>
			<h2 id="processing-title" className="sr-only">
				Latest processing status
			</h2>
			<div className="mt-6 hidden items-center lg:flex">
				{stages.map((stage, index) => (
					<div key={stage.name} className="contents">
						<div className="flex min-w-0 flex-1 items-start gap-4">
							<span className="grid size-8 shrink-0 place-items-center rounded-full bg-positive text-surface">
								<StageIcon stage={stage} />
							</span>
							<div className="min-w-0">
								<p className="font-serif text-xl leading-tight text-ink">
									{stage.name}
								</p>
								<p className="mt-1 text-sm text-text-muted">{stage.detail}</p>
							</div>
						</div>
						{index < stages.length - 1 && (
							<LuMoveRight
								className="mx-6 h-5 min-w-8 flex-1 text-text-muted/50"
								strokeWidth={1.35}
								aria-hidden="true"
							/>
						)}
					</div>
				))}
			</div>

			<div className="mt-6 lg:hidden">
				{stages.map((stage, index) => (
					<div key={stage.name} className="flex gap-4">
						<div className="flex w-8 shrink-0 flex-col items-center">
							<span className="relative z-10 grid size-8 place-items-center rounded-full bg-positive text-surface">
								<StageIcon stage={stage} />
							</span>
							{index < stages.length - 1 && (
								<span className="h-8 w-px bg-positive/65" aria-hidden="true" />
							)}
						</div>
						<div className="pb-5">
							<p className="font-serif text-xl leading-tight text-ink">
								{stage.name}
							</p>
							<p className="mt-1 text-sm text-text-muted">{stage.detail}</p>
						</div>
					</div>
				))}
			</div>
		</section>
	);
}

export default ProcessingStatus;
