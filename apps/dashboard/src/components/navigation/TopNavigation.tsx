import { useEffect, useRef, useState } from 'react';
import { NavLink } from 'react-router-dom';
import Dropdown from '@/components/ui/Dropdown';
import { useEnterprise } from '@/hooks/useEnterprise';
import { cn } from '@/utils/cn';

const navigationItems = [
	{ label: 'Overview', to: '/' },
	{ label: 'Forecast', to: '/forecast' },
	{ label: 'Health', to: '/health' },
	{ label: 'Receivables', to: '/receivables' },
	{ label: 'Planning', to: '/planning' },
	{ label: 'Data', to: '/data' },
];

function TopNavigation() {
	const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
	const mobileMenuRef = useRef<HTMLDivElement>(null);
	const mobileMenuButtonRef = useRef<HTMLButtonElement>(null);
	const { enterprise, enterpriseId, enterprises, loading, setEnterpriseId } =
		useEnterprise();
	const enterpriseOptions = enterprises.map((item) => ({
		label: item.legal_name,
		value: item.id,
	}));

	useEffect(() => {
		if (!mobileMenuOpen) return;

		function handlePointerDown(event: PointerEvent) {
			const target = event.target as Node;
			if (
				!mobileMenuRef.current?.contains(target) &&
				!mobileMenuButtonRef.current?.contains(target)
			) {
				setMobileMenuOpen(false);
			}
		}

		function handleKeyDown(event: KeyboardEvent) {
			if (event.key === 'Escape') setMobileMenuOpen(false);
		}

		document.addEventListener('pointerdown', handlePointerDown);
		document.addEventListener('keydown', handleKeyDown);
		return () => {
			document.removeEventListener('pointerdown', handlePointerDown);
			document.removeEventListener('keydown', handleKeyDown);
		};
	}, [mobileMenuOpen]);

	return (
		<header className="relative border-b border-border bg-surface">
			<nav
				className="mx-auto flex w-full items-center justify-between px-6 py-4 sm:px-10 lg:px-14"
				aria-label="Primary navigation"
			>
				<NavLink
					to="/"
					className="flex items-center gap-2 no-underline"
					onClick={() => setMobileMenuOpen(false)}
				>
					<img src="/brand/logo.svg" alt="" className="-ml-1.5 h-7 w-14" />
					<span className="text-lg font-medium tracking-tight text-ink">
						Cash Flow
					</span>
				</NavLink>

				<div className="hidden items-center gap-8 lg:flex">
					{navigationItems.map((item) => (
						<NavLink
							key={item.to}
							to={item.to}
							end={item.to === '/'}
							className={({ isActive }) =>
								cn(
									'relative flex h-10 items-center text-sm no-underline transition-colors',
									isActive
										? 'font-medium text-primary after:absolute after:-inset-x-2 after:-bottom-4 after:h-0.5 after:rounded-full after:bg-primary'
										: 'text-ink hover:text-primary',
								)
							}
						>
							{item.label}
						</NavLink>
					))}
				</div>

				<div className="flex items-center gap-4">
					<div className="hidden sm:block">
						<Dropdown
							label={enterprise?.legal_name ?? 'Select enterprise'}
							options={enterpriseOptions}
							value={enterpriseId ?? ''}
							onChange={setEnterpriseId}
							disabled={loading || enterpriseOptions.length === 0}
							className="[&>button]:text-[11px]"
							size="sm"
							variant="borderless"
						/>
					</div>
					<button
						type="button"
						ref={mobileMenuButtonRef}
						className="flex h-10 w-10 items-center justify-center rounded-control text-ink hover:bg-primary-soft lg:hidden"
						aria-label={
							mobileMenuOpen ? 'Close navigation menu' : 'Open navigation menu'
						}
						aria-expanded={mobileMenuOpen}
						aria-controls="mobile-navigation"
						onClick={() => setMobileMenuOpen((open) => !open)}
					>
						<svg
							viewBox="0 0 24 24"
							className="size-5"
							aria-hidden="true"
						>
							{mobileMenuOpen ? (
								<path
									d="m6 6 12 12M18 6 6 18"
									fill="none"
									stroke="currentColor"
									strokeLinecap="round"
									strokeWidth="1.75"
								/>
							) : (
								<path
									d="M4 7h16M4 12h16M4 17h16"
									fill="none"
									stroke="currentColor"
									strokeLinecap="round"
									strokeWidth="1.75"
								/>
							)}
						</svg>
					</button>
				</div>
			</nav>

			{mobileMenuOpen ? (
				<div
					ref={mobileMenuRef}
					id="mobile-navigation"
					className="absolute left-0 right-0 top-full z-30 border-b border-border bg-surface px-6 py-4 shadow-sm sm:px-10 lg:hidden"
				>
					<div className="mb-3 pb-3 sm:hidden">
						<Dropdown
							label={enterprise?.legal_name ?? 'Select enterprise'}
							options={enterpriseOptions}
							value={enterpriseId ?? ''}
							onChange={setEnterpriseId}
							disabled={loading || enterpriseOptions.length === 0}
							size="md"
							variant="default"
						/>
					</div>

					<div className="flex flex-col gap-1">
						{navigationItems.map((item) => (
							<NavLink
								key={item.to}
								to={item.to}
								end={item.to === '/'}
								onClick={() => setMobileMenuOpen(false)}
								className={({ isActive }) =>
									cn(
										'rounded-control px-3 py-2.5 text-sm no-underline transition-colors',
										isActive
											? 'bg-primary-soft font-medium text-primary'
											: 'text-ink hover:bg-primary-soft hover:text-primary',
									)
								}
							>
								{item.label}
							</NavLink>
						))}
					</div>
				</div>
			) : null}
		</header>
	);
}

export default TopNavigation;
