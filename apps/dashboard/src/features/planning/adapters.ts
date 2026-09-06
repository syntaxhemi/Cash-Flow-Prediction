import type { ForecastRun, SimulationRun } from '@/api/contracts';
import { formatCurrency } from '@/utils/formatCurrency';
import type { Receivable } from '@/features/receivables/types';
import type {
	PlanningCollectionOpportunity,
	PlanningDraft,
	PlanningOption,
} from './types';

type MitigationRecommendation = NonNullable<
	SimulationRun['mitigation_recommendations']
>[number];

function formatAmount(value: number) {
	return formatCurrency(value, { maximumFractionDigits: 2 });
}

function actionCopy(actionType: string) {
	switch (actionType) {
		case 'delay_capex':
			return {
				name: 'Defer discretionary investment',
				detailLabel: 'Investment outflow',
				link: 'Review investment plan',
			};
		case 'reduce_outflows':
			return {
				name: 'Tighten monthly spending',
				detailLabel: 'Monthly spending',
				link: 'Review spending plan',
			};
		case 'adjust_repayment':
			return {
				name: 'Adjust scheduled repayment',
				detailLabel: 'Scheduled repayment',
				link: 'Review repayment plan',
			};
		default:
			return {
				name: 'Review cash commitment',
				detailLabel: 'Cash commitment',
				link: 'Review draft',
			};
	}
}

function mitigationOption(
	recommendation: MitigationRecommendation,
): PlanningOption {
	const copy = actionCopy(recommendation.action_type);
	return {
		id: recommendation.id,
		name: copy.name,
		impact: Number(recommendation.expected_cashflow_delta),
		detail: `${copy.detailLabel}: ${formatAmount(Number(recommendation.original_value))} → ${formatAmount(Number(recommendation.recommended_value))}`,
		link: copy.link,
		linkHref: '#cash-position-title',
		postScenario: Number(recommendation.expected_post_action_cashflow),
		meetsBuffer: recommendation.meets_buffer,
	};
}

function buildCollectionOption(
	opportunity: PlanningCollectionOpportunity,
	baseline: number,
	buffer: number,
): PlanningOption {
	return {
		id: 'collection-opportunity',
		name: `Collect ${opportunity.name} balance`,
		impact: opportunity.impact,
		detail: `${opportunity.dueLabel} → Clear overdue balance`,
		link: 'View receivable',
		linkHref: opportunity.linkHref,
		postScenario: baseline + opportunity.impact,
		meetsBuffer: baseline + opportunity.impact >= buffer,
	};
}

function collectionOpportunity(
	receivables: Receivable[],
): PlanningCollectionOpportunity | null {
	const candidate = [...receivables].sort(
		(left, right) => Math.abs(right.predictedDelta) - Math.abs(left.predictedDelta),
	)[0];
	if (!candidate) return null;
	return {
		name: candidate.name,
		dueLabel: candidate.dueLabel,
		impact: Math.max(0, candidate.predictedDelta),
		linkHref: '/receivables',
	};
}

export type PlanningView = {
	baseline: number;
	buffer: number;
	options: PlanningOption[];
	collection: PlanningCollectionOpportunity | null;
	draft: PlanningDraft | null;
};

/** Adapts forecast, mitigation, and receivables results to the Planning design. */
export function toPlanningView(
	forecast: ForecastRun,
	mitigation: SimulationRun | null,
	receivables: Receivable[],
): PlanningView {
	const baseline = Number(forecast.predicted_net_cashflow);
	const buffer = Number(forecast.solvency_buffer);
	const collection = collectionOpportunity(receivables);
	const collectionPlan = collection
		? buildCollectionOption(collection, baseline, buffer)
		: null;
	const mitigationOptions = (mitigation?.mitigation_recommendations ?? []).map(
		(recommendation) => mitigationOption(recommendation),
	);
	const rankedOptions = [
		...(collectionPlan ? [collectionPlan] : []),
		...mitigationOptions,
	]
		.sort((left, right) => right.impact - left.impact)
		.slice(0, 3)
		.map((option, index) => ({ ...option, recommended: index === 0 }));
	const draftOption = rankedOptions[0] ?? null;
	const options = [...rankedOptions].sort(
		(left, right) => left.impact - right.impact,
	);
	const draftUsesCollection = draftOption?.id === 'collection-opportunity';

	return {
		baseline,
		buffer,
		options,
		collection,
		draft: draftOption
			? {
					name: draftOption.name,
					current: draftUsesCollection
						? collection?.dueLabel ?? 'Current plan'
						: 'Current cash plan',
					proposed: draftUsesCollection
						? 'Clear overdue balance'
						: 'Use the bounded cash plan',
					postScenario: draftOption.postScenario,
					impact: draftOption.impact,
					linkHref: draftOption.linkHref,
				}
			: null,
	};
}

/** Formats a planning amount for compact display. */
export { formatAmount };
