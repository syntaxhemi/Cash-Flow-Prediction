import { useEffect, useState, type FormEvent } from 'react';
import type {
	IngestionSource,
	IngestionSourceCredential,
	IngestionSourceCredentialCreate,
	IngestionSourceCredentialMetadataUpdate,
	IngestionSourceCredentialSecretUpdate,
	IngestionSourceCreate,
	IngestionSourceUpdate,
} from '@/api/contracts';
import Button from '@/components/ui/Button';
import InlineError from '@/components/ui/InlineError';
import Modal from '@/components/ui/Modal';

export type SourceKey = 'erpnext';
export type DataModal =
	| { type: 'add-source'; sourceKey: SourceKey }
	| { type: 'edit-source' }
	| { type: 'deactivate' };

type DataModalsProps = {
	modal: DataModal | null;
	selectedSource: IngestionSource | null;
	credential: IngestionSourceCredential | null;
	pending: boolean;
	error: Error | null;
	onClose: () => void;
	onCreateSource: (body: IngestionSourceCreate) => Promise<IngestionSource>;
	onUpdateSource: (
		sourceId: string,
		body: IngestionSourceUpdate,
	) => Promise<IngestionSource>;
	onCreateCredential: (
		sourceId: string,
		body: IngestionSourceCredentialCreate,
	) => Promise<IngestionSourceCredential>;
	onUpdateCredential: (
		sourceId: string,
		credentialId: string,
		body: IngestionSourceCredentialMetadataUpdate,
	) => Promise<IngestionSourceCredential>;
	onRotateCredential: (
		sourceId: string,
		credentialId: string,
		body: IngestionSourceCredentialSecretUpdate,
	) => Promise<IngestionSourceCredential>;
	onDeactivate: (sourceId: string) => Promise<void>;
	onSourceCreated: (source: IngestionSource) => void;
};

const fieldClass =
	'w-full rounded-control border border-border bg-surface px-3 py-2.5 text-sm text-ink outline-none focus:border-primary focus:ring-2 focus:ring-primary/15';
const labelClass = 'text-sm font-medium text-ink';

function DataModals({
	modal,
	selectedSource,
	credential,
	pending,
	error,
	onClose,
	onCreateSource,
	onUpdateSource,
	onCreateCredential,
	onUpdateCredential,
	onRotateCredential,
	onDeactivate,
	onSourceCreated,
}: DataModalsProps) {
	const [sourceKey, setSourceKey] = useState<SourceKey>('erpnext');
	const [displayName, setDisplayName] = useState('');
	const [baseUrl, setBaseUrl] = useState('');
	const [secretRef, setSecretRef] = useState('');

	useEffect(() => {
		if (!modal) return;
		if (modal.type === 'add-source') {
			setSourceKey(modal.sourceKey);
			setDisplayName('ERPNext finance ledger');
		}
		if (modal.type === 'edit-source' && selectedSource) {
			setDisplayName(selectedSource.display_name);
			const configuredUrl = credential?.config_json?.base_url;
			setBaseUrl(typeof configuredUrl === 'string' ? configuredUrl : '');
			setSecretRef('');
		}
	}, [credential, modal, selectedSource]);

	if (!modal) return null;

	async function submitSource(event: FormEvent<HTMLFormElement>) {
		event.preventDefault();
		onClose();
		const source = await onCreateSource({
			source_key: sourceKey,
			display_name: displayName.trim(),
			status: 'active',
			is_active: true,
		});
		onSourceCreated(source);
	}

	async function submitEdit(event: FormEvent<HTMLFormElement>) {
		event.preventDefault();
		if (!selectedSource) return;
		onClose();
		await onUpdateSource(selectedSource.id, {
			display_name: displayName.trim(),
		});
		if (selectedSource.source_key === 'erpnext' && baseUrl.trim()) {
			const configJson = {
				...(credential?.config_json ?? {}),
				base_url: baseUrl.trim(),
				page_size: 100,
				timeout_seconds: 15,
			};
			if (credential) {
				await onUpdateCredential(selectedSource.id, credential.id, {
					config_json: configJson,
				});
				if (secretRef.trim()) {
					await onRotateCredential(selectedSource.id, credential.id, {
						secret_ref: secretRef.trim(),
					});
				}
			} else if (secretRef.trim()) {
				await onCreateCredential(selectedSource.id, {
					credential_type: 'api_key',
					config_json: configJson,
					secret_ref: secretRef.trim(),
				});
			}
		}
	}

	async function submitDeactivate() {
		if (!selectedSource) return;
		onClose();
		await onDeactivate(selectedSource.id);
	}

	if (modal.type === 'add-source') {
		return (
			<Modal
				open
				onClose={onClose}
				title="Add a data source"
				description="Choose where the financial records should come from."
			>
				<form
					className="space-y-5"
					onSubmit={(event) => void submitSource(event).catch(() => undefined)}
				>
					<label className="block space-y-2">
						<span className={labelClass}>Display name</span>
						<input
							className={fieldClass}
							value={displayName}
							onChange={(event) => setDisplayName(event.target.value)}
							required
						/>
					</label>
					{error ? <InlineError>{error.message}</InlineError> : null}
					<div className="flex justify-end gap-3 border-t border-border/80 pt-5">
						<Button variant="muted" onClick={onClose}>Cancel</Button>
						<Button type="submit" disabled={pending}>
							{pending ? 'Adding...' : 'Add source'}
						</Button>
					</div>
				</form>
			</Modal>
		);
	}

	if (modal.type === 'edit-source') {
		return (
			<Modal
				open
				onClose={onClose}
				title="Edit data source"
				description="Update how this source appears. Its connection status is updated automatically."
			>
				<form
					className="space-y-5"
					onSubmit={(event) => void submitEdit(event).catch(() => undefined)}
				>
					<label className="block space-y-2">
						<span className={labelClass}>Display name</span>
						<input
							className={fieldClass}
							value={displayName}
							onChange={(event) => setDisplayName(event.target.value)}
							required
						/>
					</label>
					{selectedSource?.source_key === 'erpnext' ? (
						<>
							<label className="block space-y-2">
								<span className={labelClass}>ERPNext address</span>
								<input
									className={fieldClass}
									value={baseUrl}
									onChange={(event) => setBaseUrl(event.target.value)}
									placeholder="http://localhost:8090"
									type="url"
									required
								/>
							</label>
							<label className="block space-y-2">
								<span className={labelClass}>
									{credential ? 'Replace API key reference' : 'API key reference'}
								</span>
								<input
									className={fieldClass}
									value={secretRef}
									onChange={(event) => setSecretRef(event.target.value)}
									placeholder={credential ? 'Leave blank to keep the current key' : 'Enter the configured key reference'}
									type="password"
									required={!credential}
								/>
							</label>
						</>
					) : null}
					{error ? <InlineError>{error.message}</InlineError> : null}
					<div className="flex justify-end gap-3 border-t border-border/80 pt-5">
						<Button variant="muted" onClick={onClose}>Cancel</Button>
						<Button type="submit" disabled={pending}>
							{pending ? 'Saving...' : 'Save changes'}
						</Button>
					</div>
				</form>
			</Modal>
		);
	}

	if (modal.type === 'deactivate') {
		return (
			<Modal
				open
				onClose={onClose}
				title="Deactivate data source?"
				description={`New synchronizations from ${selectedSource?.display_name ?? 'this source'} will stop. Existing records are not removed.`}
			>
				{error ? <InlineError>{error.message}</InlineError> : null}
				<div className="flex justify-end gap-3 border-t border-border/80 pt-5">
					<Button variant="muted" onClick={onClose}>Keep source</Button>
					<Button
						onClick={() => void submitDeactivate().catch(() => undefined)}
						disabled={pending}
					>
						{pending ? 'Deactivating...' : 'Deactivate source'}
					</Button>
				</div>
			</Modal>
		);
	}

	return null;
}

export default DataModals;
