import { LuRefreshCw } from 'react-icons/lu';
import { cn } from '@/utils/cn';
import Button from './Button';

type ResourceErrorProps = {
	title: string;
	error: string | Error;
	onRetry?: () => void;
	className?: string;
};

/**
 * Renders a recoverable error state for a failed page or resource request.
 */
function ResourceError({
	title,
	error,
	onRetry,
	className,
}: ResourceErrorProps) {
	const message = typeof error === 'string' ? error : error.message;

	return (
		<section
			className={cn(
				'rounded-card border border-risk/30 bg-primary-soft/30 px-5 py-4 sm:px-6',
				className,
			)}
			role="alert"
		>
			<div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
				<div className="min-w-0">
					<h2 className="text-base font-semibold text-risk">{title}</h2>
					<p className="mt-1 text-sm text-text-muted">{message}</p>
				</div>
				{onRetry && (
					<Button
						size="sm"
						onClick={onRetry}
						leading={<LuRefreshCw size={14} aria-hidden="true" />}
						className="self-start border-primary text-sm sm:self-auto"
					>
						Retry
					</Button>
				)}
			</div>
		</section>
	);
}

export default ResourceError;
