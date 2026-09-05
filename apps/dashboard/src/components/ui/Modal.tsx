import { useEffect, type ReactNode } from 'react';
import { LuX } from 'react-icons/lu';
import { cn } from '@/utils/cn';

type ModalProps = {
	open: boolean;
	onClose: () => void;
	title: string;
	description?: string;
	children: ReactNode;
	footer?: ReactNode;
	className?: string;
};

/** Provides a reusable modal surface for focused dashboard workflows. */
function Modal({
	open,
	onClose,
	title,
	description,
	children,
	footer,
	className,
}: ModalProps) {
	useEffect(() => {
		if (!open) return;
		const handleKeyDown = (event: KeyboardEvent) => {
			if (event.key === 'Escape') onClose();
		};
		document.addEventListener('keydown', handleKeyDown);
		return () => document.removeEventListener('keydown', handleKeyDown);
	}, [onClose, open]);

	useEffect(() => {
		if (!open) return;
		const previousOverflow = document.body.style.overflow;
		document.body.style.overflow = 'hidden';
		return () => {
			document.body.style.overflow = previousOverflow;
		};
	}, [open]);

	if (!open) return null;

	return (
		<div
			className="fixed inset-0 z-50 grid place-items-center bg-ink/35 p-4"
			role="presentation"
			onMouseDown={(event) => {
				if (event.target === event.currentTarget) onClose();
			}}
		>
			<section
				className={cn(
					'max-h-[min(90svh,48rem)] w-full max-w-lg overflow-y-auto rounded-card border border-border bg-surface p-5 shadow-xl sm:p-6',
					className,
				)}
				role="dialog"
				aria-modal="true"
				aria-labelledby="modal-title"
			>
				<div className="flex items-start justify-between gap-5">
					<div>
						<h2 id="modal-title" className="font-serif text-2xl text-ink">
							{title}
						</h2>
						{description ? (
							<p className="mt-2 text-sm leading-relaxed text-text-muted">
								{description}
							</p>
						) : null}
					</div>
					<button
						type="button"
						className="rounded-full p-1.5 text-text-muted hover:bg-primary-soft hover:text-primary"
						onClick={onClose}
						aria-label="Close dialog"
					>
						<LuX className="size-5" aria-hidden="true" />
					</button>
				</div>
				<div className="mt-6">{children}</div>
				{footer ? (
					<div className="mt-6 flex flex-wrap justify-end gap-3 border-t border-border/80 pt-5">
						{footer}
					</div>
				) : null}
			</section>
		</div>
	);
}

export default Modal;
