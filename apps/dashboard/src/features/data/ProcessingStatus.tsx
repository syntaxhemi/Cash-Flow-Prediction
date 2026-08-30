import { LuCheck, LuMoveRight } from 'react-icons/lu';
import { processingStages } from './mock-data';
import DataSectionEyebrow from './DataSectionEyebrow';

function ProcessingStatus() {
	return (
		<section className="mt-14" aria-labelledby="processing-title">
			<DataSectionEyebrow>Latest processing</DataSectionEyebrow>
			<h2 id="processing-title" className="sr-only">
				Latest processing status
			</h2>
			<div className="mt-6 hidden items-center lg:flex">
				{processingStages.map((stage, index) => (
					<div key={stage.name} className="contents">
						<div className="flex min-w-0 flex-1 items-start gap-4">
							<span className="grid size-8 shrink-0 place-items-center rounded-full bg-positive text-surface">
								<LuCheck
									className="size-5"
									strokeWidth={2}
									aria-hidden="true"
								/>
							</span>
							<div>
								<p className="font-serif text-xl leading-tight text-ink">
									{stage.name}
								</p>
								<p className="mt-1 text-sm text-text-muted">{stage.detail}</p>
							</div>
						</div>
						{index < processingStages.length - 1 && (
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
				{processingStages.map((stage, index) => (
					<div key={stage.name} className="flex gap-4">
						<div className="flex w-8 shrink-0 flex-col items-center">
							<span className="relative z-10 grid size-8 place-items-center rounded-full bg-positive text-surface">
								<LuCheck
									className="size-5"
									strokeWidth={2}
									aria-hidden="true"
								/>
							</span>
							{index < processingStages.length - 1 && (
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
