import { NavLink } from 'react-router-dom';
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
	return (
		<header className="border-b border-border bg-surface">
			<nav
				className="mx-auto flex w-full items-center justify-between px-6 py-4 sm:px-10 lg:px-14"
				aria-label="Primary navigation"
			>
				<NavLink to="/" className="flex items-center gap-2 no-underline">
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
					<span className="hidden items-center gap-2 text-sm text-ink sm:flex">
						Northstar Manufacturing
						<span aria-hidden="true">⌄</span>
					</span>
					<button
						type="button"
						className="flex h-10 w-10 items-center justify-center rounded-control text-ink hover:bg-primary-soft lg:hidden"
						aria-label="Open navigation menu"
					>
						<span className="text-xl leading-none" aria-hidden="true">
							☰
						</span>
					</button>
				</div>
			</nav>
		</header>
	);
}

export default TopNavigation;
