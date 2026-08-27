import { cva } from 'class-variance-authority';
import { cn } from '@/utils/cn';

export type SegmentedControlOption<T extends string | number> = {
	label: string;
	value: T;
};

type SegmentedControlProps<T extends string | number> = {
	options: readonly SegmentedControlOption<T>[];
	value: T;
	onChange: (value: T) => void;
	className?: string;
	size?: 'xs' | 'sm' | 'md';
};

const segmentedControlButton = cva(
	'flex-1 whitespace-nowrap rounded-pill text-center transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-1',
	{
		variants: {
			size: {
				xs: 'px-2 py-1 text-xs',
				sm: 'px-3 py-1 text-xs',
				md: 'px-4 py-1.5 text-sm',
			},
		},
		defaultVariants: { size: 'md' },
	},
);

/**
 * Provides an accessible, mutually exclusive group of compact options.
 *
 * @param props The options, selected value, change handler, and optional class name.
 * @returns A reusable segmented control.
 */
function SegmentedControl<T extends string | number>({
	options,
	value,
	onChange,
	className,
	size = 'md',
}: SegmentedControlProps<T>) {
	return (
		<div
			className={cn(
				'flex rounded-pill border border-border p-1 text-sm',
				className,
			)}
			role="radiogroup"
		>
			{options.map((option) => {
				const isSelected = option.value === value;

				return (
					<button
						key={option.value}
						type="button"
						className={segmentedControlButton({
							size,
							className: isSelected
								? 'bg-primary text-surface'
								: 'text-text-muted hover:bg-primary-soft hover:text-ink',
						})}
						role="radio"
						aria-checked={isSelected}
						onClick={() => onChange(option.value)}
					>
						{option.label}
					</button>
				);
			})}
		</div>
	);
}

export default SegmentedControl;
