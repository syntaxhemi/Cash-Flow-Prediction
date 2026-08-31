import Button from '@/components/ui/Button';
import Dropdown from '@/components/ui/Dropdown';
import NumberInput from '@/components/ui/NumberInput';
import {
	healthComparisonOptions,
	healthScenarioInputs,
	healthScenarioOptions,
} from './scenario-options';
import type { HealthScenarioKey } from './types';

type HealthFilterBarProps = {
	scenario: HealthScenarioKey;
	scenarioValue: number;
	comparison: string;
	pending?: boolean;
	disabled?: boolean;
	onScenarioChange: (scenario: HealthScenarioKey) => void;
	onScenarioValueChange: (value: number) => void;
	onComparisonChange: (value: string) => void;
	onRun: () => void;
};

/** Renders the bounded scenario controls used by the Health page. */
function HealthFilterBar({
	scenario,
	scenarioValue,
	comparison,
	pending = false,
	disabled = false,
	onScenarioChange,
	onScenarioValueChange,
	onComparisonChange,
	onRun,
}: HealthFilterBarProps) {
	const scenarioInput = healthScenarioInputs[scenario];

	function handleScenarioChange(value: string) {
		onScenarioChange(value as HealthScenarioKey);
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
							disabled={disabled || pending}
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
						step={scenarioInput.step}
						onChange={onScenarioValueChange}
						disabled={disabled || pending}
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
						onChange={onComparisonChange}
						disabled={disabled || pending}
						className="w-full sm:w-40"
						size="sm"
					/>
				</div>
				<Button
					size="sm"
					disabled={disabled || pending}
					onClick={onRun}
					className="w-full lg:w-auto lg:shrink-0"
				>
					{pending ? 'Running…' : 'Run scenario'}
				</Button>
			</div>
		</section>
	);
}

export default HealthFilterBar;
