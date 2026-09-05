import { useCallback, useState } from 'react';
import PageLayout from '@/components/layout/PageLayout';
import InlineError from '@/components/ui/InlineError';
import ResourceError from '@/components/ui/ResourceError';
import { useEnterprise } from '@/hooks/useEnterprise';
import { useIngestionCredentials } from '@/hooks/useIngestionCredentials';
import { useIngestionMutations } from '@/hooks/useIngestionMutations';
import { useIngestionRuns } from '@/hooks/useIngestionRuns';
import { useIngestionSources } from '@/hooks/useIngestionSources';
import AddDataSection from './AddDataSection';
import DataModals, { type DataModal } from './DataModals';
import DataSectionEyebrow from './DataSectionEyebrow';
import DataSkeleton from './DataSkeleton';
import DataSourcePanel from './DataSourcePanel';
import IngestionHistory from './IngestionHistory';
import ProcessingStatus from './ProcessingStatus';

function DataPage() {
	const { enterpriseId } = useEnterprise();
	const sources = useIngestionSources(enterpriseId ?? undefined);
	const sourceItems = sources.data?.items ?? [];
	const [historyPage, setHistoryPage] = useState(0);
	const [modal, setModal] = useState<DataModal | null>(null);
	const [fileUploadError, setFileUploadError] = useState<Error | null>(null);
	const connectedSource =
		sourceItems.find((source) => source.source_key === 'erpnext') ?? null;
	const connectedRuns = useIngestionRuns(
		enterpriseId ?? undefined,
		connectedSource?.id,
		undefined,
		undefined,
		5,
		historyPage * 5,
	);
	const historyRuns = useIngestionRuns(
		enterpriseId ?? undefined,
		sourceItems.map((source) => source.id),
		undefined,
		undefined,
		5,
		historyPage * 5,
	);
	const credentials = useIngestionCredentials(
		enterpriseId ?? undefined,
		connectedSource?.id,
		'active',
	);
	const mutations = useIngestionMutations(enterpriseId ?? undefined);
	const latestRun = connectedRuns.data?.items[0] ?? null;
	const credential = credentials.data?.items[0] ?? null;
	const fileSources = sourceItems.filter(
		(source) => source.source_key === 'csv' || source.source_key === 'excel',
	);

	const refreshData = useCallback(() => {
		void sources.refresh();
		void connectedRuns.refresh();
		void historyRuns.refresh();
		void credentials.refresh();
	}, [connectedRuns, credentials, historyRuns, sources]);

	const handleSync = useCallback(() => {
		if (!connectedSource) return;
		void mutations.requestSync
			.mutateAsync({
				sourceId: connectedSource.id,
				body: { run_type: 'incremental', status: 'pending', since: null },
			})
			.then(() => {
				refreshData();
			})
			.catch(() => undefined);
	}, [connectedSource, mutations.requestSync, refreshData]);

	const handleSourceCreated = useCallback(
		() => {
			setHistoryPage(0);
			refreshData();
		},
		[refreshData],
	);

	const handleConnectErpNext = () => {
		const erpNextSource = sourceItems.find(
			(source) => source.source_key === 'erpnext',
		);
		if (erpNextSource) {
			setModal({ type: 'edit-source' });
		} else {
			setModal({ type: 'add-source', sourceKey: 'erpnext' });
		}
	};

	const handleFileSelected = (file: File | null) => {
		if (!file) return;
		setFileUploadError(null);
		const extension = file.name.split('.').pop()?.toLowerCase();
		const sourceKey = extension === 'xlsx' ? 'excel' : 'csv';
		const source = fileSources.find(
			(candidate) => candidate.source_key === sourceKey,
		);
		if (!source) {
			setFileUploadError(
				new Error('This file type is not configured for upload yet.'),
			);
			return;
		}
		void mutations.uploadFile
			.mutateAsync({ sourceId: source.id, file })
			.then(() => refreshData())
			.catch(() => undefined);
	};

	const resourceError =
		sources.error ?? connectedRuns.error ?? historyRuns.error ?? credentials.error;
	const uploadError = fileUploadError ?? mutations.uploadFile.error;
	const showSkeleton =
		sources.loading ||
		connectedRuns.loading ||
		historyRuns.loading ||
		credentials.loading;
	const modalError = modal
		? modal.type === 'add-source'
			? mutations.createSource.error
			: modal.type === 'edit-source'
				? mutations.updateSource.error
				: mutations.deleteSource.error
		: null;
	const modalPending = modal
		? modal.type === 'add-source'
			? mutations.createSource.pending
			: modal.type === 'edit-source'
				? mutations.updateSource.pending
				: mutations.deleteSource.pending
		: false;

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

				{resourceError ? (
					<ResourceError
						title="Unable to load data sources"
						error={resourceError}
						onRetry={refreshData}
						className="mt-10"
					/>
				) : null}
				{mutations.requestSync.error ? (
					<InlineError className="mt-4">
						We couldn&apos;t start the synchronization. Please try again.
					</InlineError>
				) : null}
				{uploadError ? (
					<InlineError className="mt-4">{uploadError.message}</InlineError>
				) : null}

				{showSkeleton ? (
					<DataSkeleton />
				) : (
					<>
						<section
							className={
								connectedSource
									? 'mt-10 grid gap-10 lg:grid-cols-[minmax(0,1.2fr)_minmax(0,0.8fr)] lg:gap-12 xl:grid-cols-[minmax(0,1fr)_minmax(0,1fr)]'
									: 'mt-10'
							}
							aria-label="Data sources and ingestion paths"
						>
							{connectedSource ? (
								<DataSourcePanel
									selectedSource={connectedSource}
									latestRun={latestRun}
									credential={credential}
									syncing={mutations.requestSync.pending}
									onSync={handleSync}
									onEdit={() => setModal({ type: 'edit-source' })}
									onDeactivate={() => setModal({ type: 'deactivate' })}
								/>
							) : null}
							<AddDataSection
								erpNextConnected={connectedSource?.status === 'active'}
								uploading={mutations.uploadFile.pending}
								onConnectErpNext={handleConnectErpNext}
								onFileSelected={handleFileSelected}
							/>
						</section>

						<ProcessingStatus run={latestRun} />
						<IngestionHistory
							runs={historyRuns.data?.items ?? []}
							sources={sourceItems}
							totalCount={historyRuns.data?.pagination.total_count ?? 0}
							page={historyPage}
							pageSize={5}
							onPageChange={setHistoryPage}
						/>
					</>
				)}

				<DataModals
					modal={modal}
					selectedSource={connectedSource}
					credential={credential}
					pending={modalPending}
					error={modalError}
					onClose={() => setModal(null)}
					onCreateSource={(body) => mutations.createSource.mutateAsync(body)}
					onUpdateSource={(sourceId, body) =>
						mutations.updateSource.mutateAsync({ sourceId, body }).then((result) => {
							refreshData();
							return result;
						})
					}
					onCreateCredential={(sourceId, body) =>
						mutations.createCredential
							.mutateAsync({ sourceId, body })
							.then((result) => {
								refreshData();
								return result;
							})
					}
					onUpdateCredential={(sourceId, credentialId, body) =>
						mutations.updateCredential
							.mutateAsync({ sourceId, credentialId, body })
							.then((result) => {
								refreshData();
								return result;
							})
					}
					onRotateCredential={(sourceId, credentialId, body) =>
						mutations.rotateCredential
							.mutateAsync({ sourceId, credentialId, body })
							.then((result) => {
								refreshData();
								return result;
							})
					}
					onDeactivate={(sourceId) =>
						mutations.deleteSource.mutateAsync({ sourceId }).then(() => {
							refreshData();
						})
					}
					onSourceCreated={handleSourceCreated}
				/>
			</PageLayout>
		);
}

export default DataPage;
