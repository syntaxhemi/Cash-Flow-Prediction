import type { ButtonHTMLAttributes, ReactNode } from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/utils/cn';

const buttonVariants = cva(
	'inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-pill font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
	{
		variants: {
			variant: {
				primary:
					'border border-primary bg-primary text-surface hover:bg-primary/90',
				outline:
					'border border-primary bg-surface text-primary hover:bg-primary-soft',
				soft: 'border border-primary-soft bg-primary-soft text-primary hover:border-primary',
				muted: 'border border-border bg-canvas text-ink hover:border-primary',
				ghost: 'border border-transparent text-primary hover:bg-primary-soft',
			},
			size: {
				sm: 'min-h-8 px-3 py-1.5 text-xs',
				md: 'min-h-10 px-4 py-2 text-sm',
				lg: 'min-h-11 px-5 py-2.5 text-sm',
			},
		},
		defaultVariants: {
			variant: 'primary',
			size: 'md',
		},
	},
);

type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> &
	VariantProps<typeof buttonVariants> & {
		leading?: ReactNode;
		trailing?: ReactNode;
	};

/**
 * Provides the shared button treatment and semantic visual variants.
 */
function Button({
	variant,
	size,
	leading,
	trailing,
	className,
	children,
	type = 'button',
	...props
}: ButtonProps) {
	return (
		<button
			{...props}
			type={type}
			className={cn(buttonVariants({ variant, size }), className)}
		>
			{leading}
			{children}
			{trailing}
		</button>
	);
}

export default Button;
