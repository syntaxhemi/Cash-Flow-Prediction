import { Skeleton, SkeletonText } from '@/components/ui/Skeleton';

function SummarySkeleton() {
	return (
		<section
			className="mt-14 grid gap-12 lg:grid-cols-[minmax(0,1.25fr)_minmax(20rem,0.75fr)] lg:gap-20"
			aria-hidden="true"
		>
			<Skeleton className="h-64 rounded-card bg-primary-soft" />
			<div className="pt-1 lg:pt-6">
				<SkeletonText className="h-3 w-36" />
				<Skeleton className="mt-5 h-16 w-full max-w-md" />
				<SkeletonText className="mt-4 h-12 w-full max-w-md" />
			</div>
		</section>
	);
}

function RankingSkeleton() {
	return (
		<section className="mt-16 sm:mt-20" aria-hidden="true">
			<SkeletonText className="h-3 w-36" />
			<Skeleton className="mt-3 h-9 w-64" />
			<div className="mt-8 space-y-2">
				{[0, 1, 2, 3, 4].map((index) => (
					<Skeleton key={index} className="h-20 rounded-control" />
				))}
			</div>
		</section>
	);
}

/** Renders Receivables placeholders sized to match the loaded sections. */
function ReceivablesSkeleton() {
	return (
		<div aria-busy="true" aria-label="Loading receivables">
			<SummarySkeleton />
			<RankingSkeleton />
		</div>
	);
}

export default ReceivablesSkeleton;
