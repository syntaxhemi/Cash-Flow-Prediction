import { useEffect, useId, useRef, useState } from 'react';
import type { InputHTMLAttributes } from 'react';
import { cn } from '@/utils/cn';

type NumberInputProps = Omit<
	InputHTMLAttributes<HTMLInputElement>,
	'onChange' | 'type' | 'value'
> & {
	label: string;
	value: number;
	unit?: string;
	min: number;
	max: number;
	onChange: (value: number) => void;
};

/** Renders a reusable bounded numeric input with an optional unit suffix. */
function NumberInput({
	label,
	value,
	unit,
	min,
	max,
	onChange,
	className,
	...props
}: NumberInputProps) {
	const inputId = useId();
	const descriptionId = `${inputId}-description`;
	const displayUnit = unit === 'percent' ? '%' : unit;
	const [draftValue, setDraftValue] = useState(() => String(value));
	const lastSyncedValue = useRef(value);

	useEffect(() => {
		if (value === lastSyncedValue.current) return;
		setDraftValue(String(value));
		lastSyncedValue.current = value;
	}, [value]);

	return (
		<label
			className={cn(
				'inline-flex min-w-0 flex-col items-start gap-2 sm:flex-row sm:items-center sm:gap-3',
				className,
			)}
			htmlFor={inputId}
		>
			<span className="shrink-0 text-sm font-medium text-text-muted">
				{label}
			</span>
			<div className="relative min-w-0">
				<div className="flex min-h-9 w-20 items-center rounded-pill border border-border bg-surface px-3 transition active:border-border">
					<input
						{...props}
						id={inputId}
						type="number"
						value={draftValue}
						min={min}
						max={max}
						aria-describedby={descriptionId}
						className="min-w-0 flex-1 border-0 bg-transparent p-0 text-xs text-ink shadow-none outline-none ring-0 active:border-0 active:shadow-none active:outline-none active:ring-0 focus:border-0 focus:shadow-none focus:outline-none focus:ring-0 focus-visible:border-0 focus-visible:shadow-none focus-visible:outline-none [appearance:textfield] [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none"
						onChange={(event) => {
							const rawValue = event.currentTarget.value;
							setDraftValue(rawValue);
							const nextValue = event.currentTarget.valueAsNumber;
							if (!Number.isNaN(nextValue)) {
								lastSyncedValue.current = nextValue;
								onChange(nextValue);
							}
						}}
						onBlur={(event) => {
							const nextValue = event.currentTarget.valueAsNumber;
							if (!Number.isNaN(nextValue)) {
								const boundedValue = Math.min(max, Math.max(min, nextValue));
								lastSyncedValue.current = boundedValue;
								setDraftValue(String(boundedValue));
								onChange(boundedValue);
							} else {
								lastSyncedValue.current = value;
								setDraftValue(String(value));
							}
							props.onBlur?.(event);
						}}
					/>
					{displayUnit && (
						<span className="shrink-0 text-xs text-text-muted">
							{displayUnit}
						</span>
					)}
				</div>
				<span
					id={descriptionId}
					className="absolute left-0 top-full mt-1 block whitespace-nowrap text-[10px] text-text-muted"
				>
					Range: {min}–{max}{displayUnit ? ` ${displayUnit}` : ''}
				</span>
			</div>
		</label>
	);
}

export default NumberInput;
