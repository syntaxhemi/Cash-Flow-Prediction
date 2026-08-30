export type MitigationOption = {
	name: string;
	impact: string;
	detail: string;
	link: string;
	postScenario: string;
	linkHref: string;
	recommended?: boolean;
};

export const mitigationOptions: MitigationOption[] = [
	{
		name: 'Tighten operating spend',
		impact: '+₹120K',
		detail: '₹6.35M / mo → ₹6.05M / mo',
		link: 'Review assumption',
		linkHref: '#operating-spend',
		postScenario: '₹1.70M',
	},
	{
		name: 'Defer discretionary capex',
		impact: '+₹180K',
		detail: '₹1.20M → ₹0.80M',
		link: 'Inspect outflow',
		linkHref: '#discretionary-capex',
		postScenario: '₹1.76M',
	},
	{
		name: 'Collect Apex Retail invoice',
		impact: '+₹620K',
		detail: '12 days overdue → On standard terms',
		link: 'View receivable',
		linkHref: '/receivables',
		postScenario: '₹2.20M',
		recommended: true,
	},
];
