import { useId, useRef, useState, type ChangeEvent } from 'react';
import { cn } from '@/utils/cn';

type FileUploadProps = {
	accept?: string;
	buttonLabel?: string;
	className?: string;
	onChange?: (file: File | null) => void;
};

/**
 * Provides a reusable, keyboard-accessible file selection control.
 *
 * The selected file name replaces the default button label and the selected
 * file is passed to the optional callback for view-specific handling.
 */
function FileUpload({
	accept,
	buttonLabel = 'Choose file',
	className,
	onChange,
}: FileUploadProps) {
	const inputRef = useRef<HTMLInputElement>(null);
	const inputId = useId();
	const [fileName, setFileName] = useState('');

	function handleChange(event: ChangeEvent<HTMLInputElement>) {
		const file = event.target.files?.[0] ?? null;
		setFileName(file?.name ?? '');
		onChange?.(file);
	}

	return (
		<div className={cn('max-w-full', className)}>
			<input
				ref={inputRef}
				id={inputId}
				type="file"
				accept={accept}
				className="sr-only"
				onChange={handleChange}
			/>
			<button
				type="button"
				className="max-w-full truncate rounded-control border border-border bg-surface px-4 py-2 text-sm text-ink hover:border-primary"
				onClick={() => inputRef.current?.click()}
				aria-controls={inputId}
			>
				{fileName || buttonLabel}
			</button>
		</div>
	);
}

export default FileUpload;
