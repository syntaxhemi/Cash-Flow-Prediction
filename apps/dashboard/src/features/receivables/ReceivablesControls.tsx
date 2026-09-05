import { LuArrowUpRight } from 'react-icons/lu';
import Button from '@/components/ui/Button';
import Dropdown, { type DropdownOption } from '@/components/ui/Dropdown';
import SegmentedControl from '@/components/ui/SegmentedControl';
import { horizonOptions } from './options';

const sortOptions: DropdownOption[] = [
	{ label: 'Cash impact', value: 'impact' },
	{ label: 'Outstanding amount', value: 'amount' },
	{ label: 'Payment delay', value: 'delay' },
];

const accountOptions: DropdownOption[] = [
	{ label: 'All open receivables', value: 'all' },
	{ label: 'Overdue only', value: 'overdue' },
	{ label: 'Due in 30 days', value: 'upcoming' },
];

type ReceivablesControlsProps = {
	horizon: (typeof horizonOptions)[number]['value'];
	onHorizonChange: (value: (typeof horizonOptions)[number]['value']) => void;
	sortBy: string;
	onSortChange: (value: string) => void;
	accountFilter: string;
	onAccountFilterChange: (value: string) => void;
	pending?: boolean;
	disabled?: boolean;
	onRun: () => void;
};

function ReceivablesControls({
	horizon,
	onHorizonChange,
	sortBy,
	onSortChange,
	accountFilter,
	onAccountFilterChange,
	pending = false,
	disabled = false,
	onRun,
}: ReceivablesControlsProps) {
	return (
		<section
			className="mt-10 flex flex-col gap-4 py-2 lg:flex-row lg:items-center lg:justify-between"
			aria-label="Receivables controls"
		>
			<div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:gap-4">
				<span className="text-sm font-medium text-ink">View window</span>
				<SegmentedControl
					options={horizonOptions}
					value={horizon}
					onChange={onHorizonChange}
					size="sm"
				/>
			</div>
			<div className="grid grid-cols-2 gap-3 sm:flex sm:items-center sm:gap-3">
				<Dropdown
					label="Account filter"
					options={accountOptions}
					value={accountFilter}
					onChange={onAccountFilterChange}
					disabled={disabled || pending}
					className="w-full shrink-0 sm:w-56"
					size="sm"
				/>
				<Dropdown
					label="Sort receivables"
					options={sortOptions}
					value={sortBy}
					onChange={onSortChange}
					disabled={disabled || pending}
					className="w-full shrink-0 sm:w-48"
					size="sm"
				/>
				<Button
					size="sm"
					leading={<LuArrowUpRight className="size-4" />}
					disabled={disabled || pending}
					onClick={onRun}
					className="col-span-2 w-full sm:col-span-1 sm:w-auto"
				>
					{pending ? 'Running…' : 'Run analysis'}
				</Button>
			</div>
		</section>
	);
}

export default ReceivablesControls;
