import {
	LuChevronRight,
	LuCircleCheck,
	LuFileSpreadsheet,
	LuLink,
} from 'react-icons/lu';
import FileUpload from '@/components/ui/FileUpload';
import DataIconBox from './DataIconBox';

type AddDataSectionProps = {
	erpNextConnected: boolean;
	uploading: boolean;
	onConnectErpNext: () => void;
	onFileSelected: (file: File | null) => void;
};

function AddDataSection({
	erpNextConnected,
	uploading,
	onConnectErpNext,
	onFileSelected,
}: AddDataSectionProps) {
	return (
		<section aria-labelledby="add-data-title">
			<h2
				id="add-data-title"
				className="text-xs font-semibold uppercase tracking-[0.14em] text-primary"
			>
				Add data
			</h2>
			<div className="mt-4 grid gap-4 xl:grid-cols-2 xl:gap-0">
				<article className="rounded-card border border-border/80 bg-surface p-5 xl:rounded-none xl:border-0 xl:pr-6 xl:pt-5">
					<div className="flex items-start gap-4">
						<DataIconBox icon={LuLink} />
						<div className="min-w-0">
							<h3 className="font-serif text-xl text-ink sm:text-2xl">
								Connect ERPNext
							</h3>
							<p className="mt-2 max-w-xs text-sm leading-relaxed text-text-muted">
								Use the automated accounting source
							</p>
							{erpNextConnected ? (
								<span className="mt-6 inline-flex items-center gap-2 text-sm font-medium text-positive">
									<LuCircleCheck className="size-4" aria-hidden="true" />
									Connected
								</span>
							) : (
								<button
									type="button"
									className="mt-6 inline-flex items-center gap-2 text-sm font-medium text-primary hover:underline"
									onClick={onConnectErpNext}
								>
									Connect ERPNext
									<LuChevronRight className="size-4" aria-hidden="true" />
								</button>
							)}
						</div>
					</div>
				</article>

				<article className="rounded-card border border-dashed border-text-muted/45 bg-surface p-5 xl:rounded-none xl:border-l xl:border-r-0 xl:border-t-0 xl:border-b-0 xl:border-border/80 xl:pl-6 xl:pt-5">
					<div className="flex items-start gap-4">
						<DataIconBox icon={LuFileSpreadsheet} />
						<div className="min-w-0">
							<h3 className="font-serif text-xl text-ink sm:text-2xl xl:whitespace-nowrap">
								Upload CSV or XLSX
							</h3>
							<p className="mt-2 max-w-xs text-sm leading-relaxed text-text-muted">
								Validate and preview before processing
							</p>
							<FileUpload
								className="mt-6"
								accept=".csv,.xlsx"
								loading={uploading}
								onChange={onFileSelected}
							/>
						</div>
					</div>
				</article>
			</div>
		</section>
	);
}

export default AddDataSection;
