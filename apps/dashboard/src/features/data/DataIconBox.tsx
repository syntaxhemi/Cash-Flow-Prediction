import type { IconType } from 'react-icons';

type DataIconBoxProps = {
	icon: IconType;
};

function DataIconBox({ icon: Icon }: DataIconBoxProps) {
	return (
		<span className="grid size-12 shrink-0 place-items-center rounded-control bg-primary-soft/65 text-primary sm:size-14">
			<Icon className="size-6 sm:size-7" strokeWidth={1.5} aria-hidden="true" />
		</span>
	);
}

export default DataIconBox;
