import { useCallback } from 'react';
import { api } from '@/api/client';
import type {
	IngestionSourceCredentialCreate,
	IngestionSourceCredentialMetadataUpdate,
	IngestionSourceCredentialSecretUpdate,
	IngestionRunCreate,
	IngestionSourceCreate,
	IngestionSourceUpdate,
} from '@/api/contracts';
import { useMutation } from './useMutation';

type SourceInput = { sourceId: string; body: IngestionSourceUpdate };
type SourceIdInput = { sourceId: string };
type SyncInput = { sourceId: string; body: IngestionRunCreate };
type UploadInput = { sourceId: string; file: File; sheetName?: string };
type CredentialInput = {
	sourceId: string;
	body: IngestionSourceCredentialCreate;
};
type CredentialUpdateInput = {
	sourceId: string;
	credentialId: string;
	body: IngestionSourceCredentialMetadataUpdate;
};
type CredentialRotateInput = {
	sourceId: string;
	credentialId: string;
	body: IngestionSourceCredentialSecretUpdate;
};
type CredentialIdInput = { sourceId: string; credentialId: string };

/** Exposes ingestion-source, synchronization, and upload writes. */
export function useIngestionMutations(enterpriseId: string | undefined) {
	const createSource = useMutation<
		IngestionSourceCreate,
		Awaited<ReturnType<typeof api.createIngestionSource>>
	>(
		useCallback(
			(body) =>
				enterpriseId
					? api.createIngestionSource(enterpriseId, body)
					: Promise.reject(new Error('No enterprise selected')),
			[enterpriseId],
		),
	);
	const updateSource = useMutation<
		SourceInput,
		Awaited<ReturnType<typeof api.updateIngestionSource>>
	>(
		useCallback(
			({ sourceId, body }) =>
				enterpriseId
					? api.updateIngestionSource(enterpriseId, sourceId, body)
					: Promise.reject(new Error('No enterprise selected')),
			[enterpriseId],
		),
	);
	const deleteSource = useMutation<SourceIdInput, void>(
		useCallback(
			({ sourceId }) =>
				enterpriseId
					? api.deleteIngestionSource(enterpriseId, sourceId)
					: Promise.reject(new Error('No enterprise selected')),
			[enterpriseId],
		),
	);
	const requestSync = useMutation<
		SyncInput,
		Awaited<ReturnType<typeof api.requestIngestionSync>>
	>(
		useCallback(
			({ sourceId, body }) =>
				enterpriseId
					? api.requestIngestionSync(enterpriseId, sourceId, body)
					: Promise.reject(new Error('No enterprise selected')),
			[enterpriseId],
		),
	);
	const uploadFile = useMutation<
		UploadInput,
		Awaited<ReturnType<typeof api.uploadIngestionFile>>
	>(
		useCallback(
			({ sourceId, file, sheetName }) =>
				enterpriseId
					? api.uploadIngestionFile(enterpriseId, sourceId, file, sheetName)
					: Promise.reject(new Error('No enterprise selected')),
			[enterpriseId],
		),
	);
	const createCredential = useMutation<
		CredentialInput,
		Awaited<ReturnType<typeof api.createIngestionSourceCredential>>
	>(
		useCallback(
			({ sourceId, body }) =>
				enterpriseId
					? api.createIngestionSourceCredential(enterpriseId, sourceId, body)
					: Promise.reject(new Error('No enterprise selected')),
			[enterpriseId],
		),
	);
	const updateCredential = useMutation<
		CredentialUpdateInput,
		Awaited<ReturnType<typeof api.updateIngestionSourceCredential>>
	>(
		useCallback(
			({ sourceId, credentialId, body }) =>
				enterpriseId
					? api.updateIngestionSourceCredential(
							enterpriseId,
							sourceId,
							credentialId,
							body,
						)
					: Promise.reject(new Error('No enterprise selected')),
			[enterpriseId],
		),
	);
	const rotateCredential = useMutation<
		CredentialRotateInput,
		Awaited<ReturnType<typeof api.rotateIngestionSourceCredential>>
	>(
		useCallback(
			({ sourceId, credentialId, body }) =>
				enterpriseId
					? api.rotateIngestionSourceCredential(
							enterpriseId,
							sourceId,
							credentialId,
							body,
						)
					: Promise.reject(new Error('No enterprise selected')),
			[enterpriseId],
		),
	);
	const revokeCredential = useMutation<
		CredentialIdInput,
		Awaited<ReturnType<typeof api.revokeIngestionSourceCredential>>
	>(
		useCallback(
			({ sourceId, credentialId }) =>
				enterpriseId
					? api.revokeIngestionSourceCredential(
							enterpriseId,
							sourceId,
							credentialId,
						)
					: Promise.reject(new Error('No enterprise selected')),
			[enterpriseId],
		),
	);

	return {
		createSource,
		updateSource,
		deleteSource,
		requestSync,
		uploadFile,
		createCredential,
		updateCredential,
		rotateCredential,
		revokeCredential,
	};
}
