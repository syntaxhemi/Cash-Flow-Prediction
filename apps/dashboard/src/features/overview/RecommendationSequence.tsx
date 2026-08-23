import { Link } from 'react-router-dom';
import { cn } from '@/utils/cn';
import type { Recommendation } from './types';

type RecommendationSequenceProps = {
	recommendations: Recommendation[];
	className?: string;
};

function RecommendationSequence({
	recommendations,
	className,
}: RecommendationSequenceProps) {
	return (
		<section
			aria-labelledby="recommendations-title"
			className={cn('mt-16 lg:mt-24', className)}
		>
			<p
				id="recommendations-title"
				className="text-xs font-semibold uppercase tracking-widest text-primary"
			>
				Recommended next
			</p>
			<div className="mt-5 flex flex-wrap">
				{recommendations.map((recommendation) => (
					<article
						key={recommendation.number}
						className={
							recommendation.featured
								? 'flex basis-full items-start gap-5 rounded-card bg-primary-soft/50 px-6 py-6 sm:px-8 lg:px-10'
								: 'flex items-start gap-5 py-7 lg:w-[49%] lg:align-top lg:pr-10'
						}
					>
						<div className="w-13 shrink-0 font-serif text-4xl leading-none text-primary sm:w-17.5 sm:text-5xl">
							{recommendation.number}
						</div>
						<div>
							<h3 className="font-serif text-[21px] leading-tight text-ink sm:text-2xl">
								{recommendation.title}
							</h3>
							<p className="mt-2 max-w-xl text-sm leading-6 text-text-muted">
								{recommendation.detail}
							</p>
							<Link
								to={recommendation.to}
								className="mt-4 inline-flex border-b border-transparent pb-px text-sm font-medium text-primary no-underline hover:border-primary"
							>
								<span>
									{recommendation.action}{' '}
									<span className="ml-2" aria-hidden="true">
										→
									</span>
								</span>
							</Link>
						</div>
					</article>
				))}
			</div>
		</section>
	);
}

export default RecommendationSequence;
