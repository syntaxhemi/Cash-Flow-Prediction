import { useEffect, useId, useMemo, useRef, useState } from 'react';
import { cva } from 'class-variance-authority';
import { cn } from '@/utils/cn';

type DatePickerProps = {
	value: Date;
	onChange: (value: Date) => void;
	label?: string;
	displayValue?: string;
	className?: string;
	popoverClassName?: string;
	size?: 'sm' | 'md';
};

const datePickerButton = cva(
	'inline-flex items-center rounded-pill border border-border bg-surface text-left text-ink transition hover:border-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary',
	{
		variants: {
			size: {
				sm: 'min-h-9 gap-2 px-3 py-1.5 text-xs',
				md: 'min-h-10 gap-3 px-4 py-2 text-sm',
			},
		},
		defaultVariants: { size: 'md' },
	},
);

const weekdays = ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'];

function sameDay(first: Date, second: Date) {
	return first.toDateString() === second.toDateString();
}

function monthDays(month: Date) {
	const first = new Date(month.getFullYear(), month.getMonth(), 1);
	const start = new Date(first);
	start.setDate(first.getDate() - first.getDay());
	const count = new Date(
		month.getFullYear(),
		month.getMonth() + 1,
		0,
	).getDate();
	return Array.from(
		{ length: Math.ceil((start.getDay() + count) / 7) * 7 },
		(_, index) => {
			const day = new Date(start);
			day.setDate(start.getDate() + index);
			return day;
		},
	);
}

function formatDate(value: Date) {
	return value.toLocaleDateString('en-IN', {
		day: 'numeric',
		month: 'short',
		year: 'numeric',
	});
}

function CalendarIcon() {
	return (
		<svg
			viewBox="0 0 20 20"
			className="size-4 shrink-0 text-text-muted"
			aria-hidden="true"
		>
			<rect
				x="3"
				y="4.5"
				width="14"
				height="12"
				rx="2"
				fill="none"
				stroke="currentColor"
				strokeWidth="1.5"
			/>
			<path
				d="M6 3v3M14 3v3M3 8h14"
				fill="none"
				stroke="currentColor"
				strokeLinecap="round"
				strokeWidth="1.5"
			/>
		</svg>
	);
}

/**
 * Renders a reusable date field with an inline calendar popover.
 *
 * Selecting a day immediately calls `onChange` and closes the popover. By
 * default the field displays one date; `displayValue` can provide a formatted
 * range or another view-specific representation without changing the picker.
 */
function DatePicker({
	value,
	onChange,
	label = 'date',
	displayValue,
	className,
	popoverClassName,
	size = 'md',
}: DatePickerProps) {
	const [isOpen, setIsOpen] = useState(false);
	const [selectionView, setSelectionView] = useState<
		'days' | 'months' | 'years'
	>('days');
	const [visibleMonth, setVisibleMonth] = useState(
		new Date(value.getFullYear(), value.getMonth(), 1),
	);
	const containerRef = useRef<HTMLDivElement>(null);
	const dialogId = useId();
	const days = useMemo(() => monthDays(visibleMonth), [visibleMonth]);

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

	function openPicker() {
		setVisibleMonth(new Date(value.getFullYear(), value.getMonth(), 1));
		setSelectionView('days');
		setIsOpen(true);
	}

	function shiftMonth(offset: number) {
		setVisibleMonth(
			(current) =>
				new Date(current.getFullYear(), current.getMonth() + offset, 1),
		);
	}

	function selectDay(day: Date) {
		onChange(day);
		setIsOpen(false);
	}

	function selectMonth(month: number) {
		setVisibleMonth((current) => new Date(current.getFullYear(), month, 1));
		setSelectionView('days');
	}

	function selectYear(year: number) {
		setVisibleMonth((current) => new Date(year, current.getMonth(), 1));
		setSelectionView('months');
	}

	return (
		<div
			ref={containerRef}
			className={cn('relative inline-block w-max max-w-full', className)}
		>
			<button
				type="button"
				className={cn(datePickerButton({ size }), 'w-full')}
				aria-haspopup="dialog"
				aria-expanded={isOpen}
				aria-controls={dialogId}
				onClick={() => (isOpen ? setIsOpen(false) : openPicker())}
			>
				<CalendarIcon />
				<span className="truncate">{displayValue ?? formatDate(value)}</span>
			</button>
			{isOpen && (
				<div
					id={dialogId}
					className={cn(
						'absolute left-0 top-full z-30 mt-2 w-72 rounded-card border border-border bg-surface p-4 shadow-sm',
						popoverClassName,
					)}
					role="dialog"
					aria-label={`Select ${label}`}
				>
					<div className="flex items-center justify-between">
						<button
							type="button"
							className="rounded-control px-2 py-1 text-lg text-text-muted hover:bg-primary-soft"
							onClick={() => shiftMonth(-1)}
							aria-label="Previous month"
						>
							‹
						</button>
						<div className="flex items-center gap-0">
							<button
								type="button"
								className={cn(
									'rounded-control px-1 py-1 text-sm font-medium text-ink hover:bg-primary-soft',
									selectionView === 'months' && 'bg-primary-soft text-primary',
								)}
								onClick={() =>
									setSelectionView(
										selectionView === 'months' ? 'days' : 'months',
									)
								}
							>
								{visibleMonth.toLocaleDateString('en-IN', { month: 'long' })}
							</button>
							<button
								type="button"
								className={cn(
									'rounded-control px-1 py-1 text-sm font-medium text-ink hover:bg-primary-soft',
									selectionView === 'years' && 'bg-primary-soft text-primary',
								)}
								onClick={() =>
									setSelectionView(selectionView === 'years' ? 'days' : 'years')
								}
							>
								{visibleMonth.getFullYear()}
							</button>
						</div>
						<button
							type="button"
							className="rounded-control px-2 py-1 text-lg text-text-muted hover:bg-primary-soft"
							onClick={() => shiftMonth(1)}
							aria-label="Next month"
						>
							›
						</button>
					</div>
					{selectionView === 'days' && (
						<div className="mt-4 grid grid-cols-7 text-center text-xs font-medium text-text-muted">
							{weekdays.map((weekday) => (
								<span key={weekday}>{weekday}</span>
							))}
						</div>
					)}
					{selectionView === 'days' && (
						<div className="mt-2 grid grid-cols-7 gap-1">
							{days.map((day) => {
								const isCurrentMonth =
									day.getMonth() === visibleMonth.getMonth();
								return (
									<button
										key={day.toISOString()}
										type="button"
										className={cn(
											'grid aspect-square place-items-center rounded-control text-sm',
											isCurrentMonth
												? 'text-ink hover:bg-primary-soft'
												: 'text-text-muted/40',
											sameDay(day, value) &&
												'bg-primary font-medium text-surface hover:bg-primary',
										)}
										onClick={() => selectDay(day)}
										aria-label={formatDate(day)}
									>
										{day.getDate()}
									</button>
								);
							})}
						</div>
					)}
					{selectionView === 'months' && (
						<div className="mt-4 grid grid-cols-3 gap-2">
							{Array.from({ length: 12 }, (_, month) => {
								const label = new Date(2025, month, 1).toLocaleDateString(
									'en-IN',
									{ month: 'short' },
								);
								return (
									<button
										key={label}
										type="button"
										className={cn(
											'rounded-control py-2 text-sm text-ink hover:bg-primary-soft',
											month === visibleMonth.getMonth() &&
												'bg-primary text-surface hover:bg-primary',
										)}
										onClick={() => selectMonth(month)}
									>
										{label}
									</button>
								);
							})}
						</div>
					)}
					{selectionView === 'years' && (
						<div className="mt-4 grid grid-cols-3 gap-2">
							{Array.from({ length: 12 }, (_, index) => {
								const year = visibleMonth.getFullYear() - 5 + index;
								return (
									<button
										key={year}
										type="button"
										className={cn(
											'rounded-control py-2 text-sm text-ink hover:bg-primary-soft',
											year === visibleMonth.getFullYear() &&
												'bg-primary text-surface hover:bg-primary',
										)}
										onClick={() => selectYear(year)}
									>
										{year}
									</button>
								);
							})}
						</div>
					)}
				</div>
			)}
		</div>
	);
}

export default DatePicker;
