import type {
	ForecastObservationDriver,
	HealthDeltaRequest,
	SimulationRun,
} from '@/api/contracts';
import { formatCurrency } from '@/utils/formatCurrency';
import type { HealthPageData, HealthScenarioKey } from './types';
import { healthScenarioOptions } from './scenario-options';

const healthStatusLabels: Record<string, string> = {
	comfortable: 'Comfortable',
	at_risk: 'At risk',
	critical: 'Critical',
};

const preciseCurrencyOptions = { maximumFractionDigits: 2 };

function numberValue(value: unknown) {
	if (typeof value !== 'string' && typeof value !== 'number') return null;
	const parsed = Number(value);
	return Number.isFinite(parsed) ? parsed : null;
}

function signedCurrency(value: number) {
	const formatted = formatCurrency(value, preciseCurrencyOptions);
	return value > 0 ? `+${formatted}` : formatted.replace('-', '−');
}

function signedPoints(value: number) {
	const formatted = `${Math.abs(value).toLocaleString('en-IN', {
		maximumFractionDigits: 2,
	})} health points`;
	if (value > 0) return `+${formatted}`;
	if (value < 0) return `−${formatted}`;
	return formatted;
}

function scenarioLabel(scenario: HealthScenarioKey) {
	return (
		healthScenarioOptions.find((option) => option.value === scenario)?.label ??
		scenario
	);
}

function scenarioFromRun(run: SimulationRun, scenario: HealthScenarioKey) {
	const matchingScenario = run.scenarios?.find(
		(item) => scenario in item.input_patch_json,
	);
	if (matchingScenario) return matchingScenario;
	return run.scenarios && run.scenarios.length > 1 ? run.scenarios[0] : null;
}

function observationDriverTitle(driver: ForecastObservationDriver) {
	const titles: Record<string, string> = {
		Receivables: 'Invoice value',
		Collections: 'Recorded inflows',
		'Operating costs': 'Recorded outflows',
	};
	return titles[driver.label] ?? driver.label;
}

function observationDriverImpacts(
	drivers: ForecastObservationDriver[],
): HealthPageData['impacts'] {
	return drivers.slice(0, 3).map((driver, index) => ({
		label: driver.label,
		amount: formatCurrency(Number(driver.value), preciseCurrencyOptions),
		title: observationDriverTitle(driver),
		detail: driver.detail,
		tone: index === 0 ? 'featured' : index === 1 ? 'neutral' : 'soft',
	}));
}

/** Adapts a completed health simulation into the existing Health page view model. */
export function toHealthView(
	run: SimulationRun,
	forecastPrediction: number,
	scenario: HealthScenarioKey,
	observationDrivers: ForecastObservationDriver[] = [],
): HealthPageData | null {
	const scenarioResult = scenarioFromRun(run, scenario);
	const baselineScore = numberValue(run.summary_result.baseline_health_score);
	const scenarioScore = numberValue(scenarioResult?.health_score);
	const scenarioDelta = numberValue(scenarioResult?.health_score_delta);
	const cashflowDelta = numberValue(scenarioResult?.delta_from_baseline);
	const predictedCashflow = numberValue(scenarioResult?.predicted_net_cashflow);

	if (
		!scenarioResult ||
		baselineScore === null ||
		scenarioScore === null ||
		scenarioDelta === null ||
		cashflowDelta === null ||
		predictedCashflow === null
	) {
		return null;
	}

	const label = scenarioLabel(scenario);
	const status =
		healthStatusLabels[scenarioResult.health_status ?? ''] ?? 'Unrated';
	const buffer = numberValue(run.summary_result.solvency_buffer) ?? 0;
	const bufferGap = predictedCashflow - buffer;

	return {
		stats: [
			{
				label: 'Cash delta',
				value: signedCurrency(cashflowDelta),
				tone: 'primary',
				supporting: `${label} target · ${scenarioResult.input_patch_json[scenario] ?? 'selected value'}`,
			},
			{
				label: 'Baseline cash',
				value: formatCurrency(forecastPrediction, preciseCurrencyOptions),
			},
			{
				label: 'Simulated cash',
				value: formatCurrency(predictedCashflow, preciseCurrencyOptions),
				tone: 'primary',
			},
			{
				label: 'Above buffer',
				value: signedCurrency(bufferGap),
				tone: 'primary',
			},
		],
		scores: [
			{
				label: 'Baseline',
				score: baselineScore,
				status: 'Baseline',
				tone: 'primary',
			},
			{
				label,
				score: scenarioScore,
				status,
				tone: 'soft',
			},
		],
		healthDelta: signedPoints(scenarioDelta),
		healthDeltaValue: scenarioDelta,
		impacts: observationDriverImpacts(observationDrivers),
	};
}

/** Builds the single-feature request issued by the Health page controls. */
export function toHealthRequest(
	scenario: HealthScenarioKey,
	value: number,
): HealthDeltaRequest {
	return {
		profile: 'custom',
		features: { [scenario]: value },
	};
}
