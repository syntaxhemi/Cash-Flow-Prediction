import { useEffect, useId, useRef, useState } from 'react';
import { cva } from 'class-variance-authority';
import { cn } from '@/utils/cn';

export type DropdownOption = {
	label: string;
	value: string;
};

type DropdownProps = {
	label: string;
	options: DropdownOption[];
	value: string;
	onChange: (value: string) => void;
	className?: string;
	size?: 'sm' | 'md';
};

const dropdownButton = cva(
	'inline-flex w-full items-center justify-between rounded-pill border border-border bg-surface text-left text-ink transition hover:border-border active:border-border focus:border-border focus-visible:border-border focus-visible:outline-none focus-visible:ring-0',
	{
		variants: {
			size: {
				sm: 'min-h-9 gap-3 px-3 py-1.5 text-xs',
				md: 'min-h-10 gap-4 px-4 py-2 text-sm',
			},
		},
		defaultVariants: { size: 'md' },
	},
);

function ChevronDown() {
	return (
		<svg viewBox="0 0 16 16" className="size-4 shrink-0" aria-hidden="true">
			<path
				d="m4 6 4 4 4-4"
				fill="none"
				stroke="currentColor"
				strokeLinecap="round"
				strokeLinejoin="round"
				strokeWidth="1.5"
			/>
		</svg>
	);
}

/**
 * Renders a reusable accessible dropdown whose width follows its parent.
 */
function Dropdown({
	label,
	options,
	value,
	onChange,
	className,
	size = 'md',
}: DropdownProps) {
	const [isOpen, setIsOpen] = useState(false);
	const containerRef = useRef<HTMLDivElement>(null);
	const listboxId = useId();
	const selectedOption =
		options.find((option) => option.value === value) ?? options[0];

	useEffect(() => {
		if (!isOpen) return;

		function handlePointerDown(event: PointerEvent) {
			if (!containerRef.current?.contains(event.target as Node))
				setIsOpen(false);
		}

		function handleKeyDown(event: KeyboardEvent) {
			if (event.key === 'Escape') setIsOpen(false);
		}

		document.addEventListener('pointerdown', handlePointerDown);
		document.addEventListener('keydown', handleKeyDown);
		return () => {
			document.removeEventListener('pointerdown', handlePointerDown);
			document.removeEventListener('keydown', handleKeyDown);
		};
	}, [isOpen]);

	return (
		<div
			ref={containerRef}
			className={cn('relative inline-block w-max max-w-full', className)}
		>
			<button
				type="button"
				className={dropdownButton({ size })}
				aria-haspopup="listbox"
				aria-expanded={isOpen}
				aria-controls={listboxId}
				onClick={() => setIsOpen((open) => !open)}
			>
				<span>{selectedOption?.label ?? label}</span>
				<ChevronDown />
			</button>
			{isOpen && (
				<ul
					id={listboxId}
					className="absolute left-0 top-full z-20 mt-2 min-w-full space-y-1 rounded-card border border-border bg-surface p-1 shadow-sm"
					role="listbox"
					aria-label={label}
				>
					{options.map((option) => (
						<li key={option.value}>
							<button
								type="button"
								className={cn(
									'w-full rounded-control px-3 py-2 text-left text-sm text-ink hover:bg-primary-soft',
									option.value === value &&
										'bg-primary-soft font-medium text-primary',
								)}
								role="option"
								aria-selected={option.value === value}
								onClick={() => {
									onChange(option.value);
									setIsOpen(false);
								}}
							>
								{option.label}
							</button>
						</li>
					))}
				</ul>
			)}
		</div>
	);
}

export default Dropdown;
