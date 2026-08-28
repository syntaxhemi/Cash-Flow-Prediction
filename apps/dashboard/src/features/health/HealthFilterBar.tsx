import { useState } from 'react';
import Button from '@/components/ui/Button';
import Dropdown from '@/components/ui/Dropdown';
import NumberInput from '@/components/ui/NumberInput';
import {
	healthComparisonOptions,
	healthScenarioInputs,
	healthScenarioOptions,
} from './mock-data';
import type { HealthScenarioKey } from './types';

/** Renders the bounded scenario controls used by the Health page. */
function HealthFilterBar() {
	const [scenario, setScenario] = useState<HealthScenarioKey>(
		'delayed-collections',
	);
	const [scenarioValue, setScenarioValue] = useState(
		healthScenarioInputs['delayed-collections'].defaultValue,
	);
	const [comparison, setComparison] = useState<string>(
		healthComparisonOptions[0].value,
	);
	const scenarioInput = healthScenarioInputs[scenario];

	function handleScenarioChange(value: string) {
		const nextScenario = value as HealthScenarioKey;
		setScenario(nextScenario);
		setScenarioValue(healthScenarioInputs[nextScenario].defaultValue);
	}

	return (
		<section className="mt-10" aria-label="Health scenario controls">
			<div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:gap-6">
				<div className="flex min-w-0 flex-row items-end gap-3 sm:items-center">
					<div className="flex min-w-0 flex-1 flex-col gap-2 sm:flex-row sm:items-center sm:gap-3">
						<span className="text-sm font-medium text-text-muted">
							Scenario
						</span>
						<Dropdown
							label="Scenario"
							options={healthScenarioOptions}
							value={scenario}
							onChange={handleScenarioChange}
							className="w-full min-w-0 sm:w-52"
							size="sm"
						/>
					</div>
					<NumberInput
						label={scenarioInput.label}
						value={scenarioValue}
						unit={scenarioInput.unit}
						min={scenarioInput.min}
						max={scenarioInput.max}
						onChange={setScenarioValue}
						className="w-auto shrink-0 sm:flex-row sm:items-center sm:gap-3"
					/>
				</div>
				<div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:gap-3">
					<span className="text-sm font-medium text-text-muted">
						Compare with
					</span>
					<Dropdown
						label="Compare with"
						options={healthComparisonOptions}
						value={comparison}
						onChange={setComparison}
						className="w-full sm:w-40"
						size="sm"
					/>
				</div>
				<Button size="sm" className="w-full lg:w-auto lg:shrink-0">
					Run scenario
				</Button>
			</div>
		</section>
	);
}

export default HealthFilterBar;
