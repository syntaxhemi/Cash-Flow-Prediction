import type { HTMLAttributes } from 'react';
import { cn } from '@/utils/cn';

/** Renders the base animated placeholder used by loading states. */
export function Skeleton({
	className,
	...props
}: HTMLAttributes<HTMLSpanElement>) {
	return (
		<span
			aria-hidden="true"
			{...props}
			className={cn('block animate-pulse rounded-control bg-border', className)}
		/>
	);
}

/** Renders a one-line text placeholder. */
export function SkeletonText({
	className,
	...props
}: HTMLAttributes<HTMLSpanElement>) {
	return <Skeleton {...props} className={cn('h-4', className)} />;
}

/** Renders a circular placeholder, useful for avatars and icons. */
export function SkeletonCircle({
	className,
	...props
}: HTMLAttributes<HTMLSpanElement>) {
	return (
		<Skeleton {...props} className={cn('size-10 rounded-full', className)} />
	);
}

/** Renders a placeholder with the shared control height and radius. */
export function SkeletonControl({
	className,
	...props
}: HTMLAttributes<HTMLSpanElement>) {
	return (
		<Skeleton {...props} className={cn('h-10 rounded-control', className)} />
	);
}
