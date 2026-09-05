export type PlanningOption = {
	id: string;
	name: string;
	impact: number;
	detail: string;
	link: string;
	linkHref: string;
	postScenario: number;
	meetsBuffer: boolean;
	recommended?: boolean;
};

export type PlanningCollectionOpportunity = {
	name: string;
	dueLabel: string;
	impact: number;
	linkHref: string;
};

export type PlanningDraft = {
	name: string;
	current: string;
	proposed: string;
	postScenario: number;
	impact: number;
	linkHref: string;
};
