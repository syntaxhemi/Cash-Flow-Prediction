import { useMemo, useState } from 'react';
import Button from '@/components/ui/Button';
import DatePicker from '@/components/ui/DatePicker';
import SegmentedControl from '@/components/ui/SegmentedControl';

const horizonOptions = [30, 60, 90] as const;
const mobileHorizonOptions = horizonOptions.map((option) => ({
	label: `${option}d`,
	value: option,
}));

export type ForecastRange = { startDate: Date; endDate: Date };

type ForecastFilterBarProps = {
	pending?: boolean;
	disabled?: boolean;
	onRun?: (range: ForecastRange) => void;
};

function addDays(date: Date, days: number) {
	const result = new Date(date);
	result.setDate(result.getDate() + days);
	return result;
}

function startOfCurrentMonth() {
	const now = new Date();
	return new Date(now.getFullYear(), now.getMonth(), 1);
}

function formatRange(startDate: Date, horizon: number) {
	const endDate = addDays(startDate, horizon);
	const format = (date: Date) =>
		date.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
	return `${format(startDate)} — ${format(endDate)}`;
}

/**
 * Provides the Forecast page's horizon and date controls.
 *
 * The date field controls the start date, while the selected horizon derives the
 * end date passed to the forecast request.
 */
function ForecastFilterBar({
	pending = false,
	disabled = false,
	onRun,
}: ForecastFilterBarProps) {
	const [startDate, setStartDate] = useState(startOfCurrentMonth);
	const [horizon, setHorizon] = useState<(typeof horizonOptions)[number]>(30);
	const rangeLabel = useMemo(
		() => formatRange(startDate, horizon),
		[startDate, horizon],
	);
	const run = () =>
		onRun?.({ startDate, endDate: addDays(startDate, horizon) });

	return (
		<section className="mt-10" aria-label="Forecast controls">
			<div className="hidden items-center justify-between gap-6 md:flex">
				<div className="flex items-center gap-3">
					<span className="text-sm font-medium text-ink">Forecast horizon</span>
					<DatePicker
						value={startDate}
						onChange={setStartDate}
						label="forecast start date"
						displayValue={rangeLabel}
						className="w-44"
						size="sm"
					/>
					<SegmentedControl
						options={horizonOptions.map((option) => ({
							label: `${option} days`,
							value: option,
						}))}
						value={horizon}
						onChange={setHorizon}
						size="sm"
					/>
				</div>
				<Button size="sm" onClick={run} disabled={disabled || pending}>
					{pending ? 'Running…' : 'Run forecast'}
				</Button>
			</div>
			<div className="flex flex-col gap-4 md:hidden">
				<div className="grid grid-cols-2 gap-3">
					<DatePicker
						value={startDate}
						onChange={setStartDate}
						label="forecast start date"
						displayValue={rangeLabel}
						className="w-full"
						popoverClassName="max-lg:left-0 max-lg:right-auto"
					/>
					<SegmentedControl
						options={mobileHorizonOptions}
						value={horizon}
						onChange={setHorizon}
						size="xs"
						className="w-full"
					/>
				</div>
				<Button
					size="lg"
					className="w-full"
					onClick={run}
					disabled={disabled || pending}
				>
					{pending ? 'Running…' : 'Run forecast'}
				</Button>
			</div>
		</section>
	);
}

export default ForecastFilterBar;
