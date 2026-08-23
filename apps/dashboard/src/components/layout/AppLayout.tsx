import { Outlet } from 'react-router-dom';
import TopNavigation from '@/components/navigation/TopNavigation';

function AppLayout() {
	return (
		<div className="min-h-svh bg-surface text-ink">
			<TopNavigation />
			<Outlet />
		</div>
	);
}

export default AppLayout;
