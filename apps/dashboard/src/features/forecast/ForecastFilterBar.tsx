import { useMemo, useState } from 'react';
import Button from '@/components/ui/Button';
import DatePicker from '@/components/ui/DatePicker';
import Dropdown, { type DropdownOption } from '@/components/ui/Dropdown';
import SegmentedControl from '@/components/ui/SegmentedControl';

const horizonOptions = [30, 60, 90] as const;
const mobileHorizonOptions = horizonOptions.map((option) => ({
	label: `${option}d`,
	value: option,
}));
const scenarioOptions: DropdownOption[] = [
	{ label: 'Baseline', value: 'baseline' },
	{ label: 'Conservative', value: 'conservative' },
	{ label: 'Optimistic', value: 'optimistic' },
];
const customScenarioOptions: DropdownOption[] = [
	{ label: 'None', value: 'none' },
	{ label: 'Delayed collections', value: 'delayed-collections' },
	{ label: 'Earlier collections', value: 'earlier-collections' },
];

function addDays(date: Date, days: number) {
	const result = new Date(date);
	result.setDate(result.getDate() + days);
	return result;
}

function formatRange(startDate: Date, horizon: number) {
	const endDate = addDays(startDate, horizon);
	const format = (date: Date) =>
		date.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
	return `${format(startDate)} — ${format(endDate)}`;
}

/**
 * Provides the Forecast page's horizon, date, and scenario controls.
 *
 * The date field controls the start date, while the selected horizon derives the
 * displayed end date so the page can later pass a normalized range to the API.
 */
function ForecastFilterBar() {
	const [startDate, setStartDate] = useState(new Date(2025, 4, 13));
	const [horizon, setHorizon] = useState<(typeof horizonOptions)[number]>(30);
	const [scenario, setScenario] = useState('baseline');
	const [customScenario, setCustomScenario] = useState('none');
	const rangeLabel = useMemo(
		() => formatRange(startDate, horizon),
		[startDate, horizon],
	);

	return (
		<section className="mt-10" aria-label="Forecast controls">
			<div className="hidden items-center justify-between gap-6 lg:flex">
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
				<div className="flex items-center gap-3">
					<span className="text-sm font-medium text-ink">Scenario</span>
					<Dropdown
						label="Scenario"
						options={scenarioOptions}
						value={scenario}
						onChange={setScenario}
						className="w-40"
						size="sm"
					/>
					<span className="text-sm font-medium text-ink">Custom Scenario</span>
					<Dropdown
						label="Custom Scenario"
						options={customScenarioOptions}
						value={customScenario}
						onChange={setCustomScenario}
						className="w-40"
						size="sm"
					/>
					<Button size="sm">Run forecast</Button>
				</div>
			</div>
			<div className="flex flex-col gap-4 lg:hidden">
				<div className="grid grid-cols-2 gap-3">
					<SegmentedControl
						options={mobileHorizonOptions}
						value={horizon}
						onChange={setHorizon}
						size="xs"
						className="w-full"
					/>
					<DatePicker
						value={startDate}
						onChange={setStartDate}
						label="forecast start date"
						displayValue={rangeLabel}
						className="w-full"
						popoverClassName="max-lg:left-auto max-lg:right-0"
					/>
				</div>
				<div className="grid grid-cols-2 gap-3">
					<Dropdown
						label="Scenario"
						options={scenarioOptions}
						value={scenario}
						onChange={setScenario}
						className="w-full"
					/>
					<Dropdown
						label="Compare scenario"
						options={customScenarioOptions}
						value={customScenario}
						onChange={setCustomScenario}
						className="w-full"
					/>
				</div>
				<Button size="lg" className="w-full">
					Run forecast
				</Button>
			</div>
		</section>
	);
}

export default ForecastFilterBar;
