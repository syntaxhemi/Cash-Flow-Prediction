import PageLayout from '@/components/layout/PageLayout';
import AddDataSection from './AddDataSection';
import DataSectionEyebrow from './DataSectionEyebrow';
import DataSourcePanel from './DataSourcePanel';
import IngestionHistory from './IngestionHistory';
import ProcessingStatus from './ProcessingStatus';

function DataPage() {
	return (
		<PageLayout title="Data">
			<header>
				<DataSectionEyebrow>Data</DataSectionEyebrow>
				<h1 className="mt-3 font-serif text-4xl leading-none text-ink sm:text-5xl">
					Data &amp; Ingestion
				</h1>
				<p className="mt-4 max-w-2xl text-base leading-relaxed text-text-muted sm:text-lg">
					Connect financial data, validate records, and keep the cash outlook
					current.
				</p>
			</header>

			<section
				className="mt-10 grid gap-10 lg:grid-cols-[minmax(0,1.2fr)_minmax(0,0.8fr)] lg:gap-12 xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]"
				aria-label="Data sources and ingestion paths"
			>
				<DataSourcePanel />
				<AddDataSection />
			</section>

			<ProcessingStatus />
			<IngestionHistory />
		</PageLayout>
	);
}

export default DataPage;
