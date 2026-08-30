import type { ReactNode } from 'react';
import { cn } from '@/utils/cn';

type InlineErrorProps = {
	children: ReactNode;
	className?: string;
};

/**
 * Renders a compact error message alongside the action or field that failed.
 */
function InlineError({ children, className }: InlineErrorProps) {
	return (
		<p className={cn('text-sm text-risk', className)} role="alert">
			{children}
		</p>
	);
}

export default InlineError;
