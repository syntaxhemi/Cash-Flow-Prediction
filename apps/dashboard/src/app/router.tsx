import { createBrowserRouter } from 'react-router-dom';
import AppLayout from '@/components/layout/AppLayout';
import DataPage from '@/features/data/DataPage';
import ForecastPage from '@/features/forecast/ForecastPage';
import HealthPage from '@/features/health/HealthPage';
import OverviewPage from '@/features/overview/OverviewPage';
import PlanningPage from '@/features/planning/PlanningPage';
import ReceivablesPage from '@/features/receivables/ReceivablesPage';

export const router = createBrowserRouter([
	{
		path: '/',
		Component: AppLayout,
		children: [
			{
				index: true,
				Component: OverviewPage,
				handle: { title: 'Overview' },
			},
			{
				path: 'forecast',
				Component: ForecastPage,
				handle: { title: 'Forecast' },
			},
			{
				path: 'health',
				Component: HealthPage,
				handle: { title: 'Health' },
			},
			{
				path: 'receivables',
				Component: ReceivablesPage,
				handle: { title: 'Receivables' },
			},
			{
				path: 'planning',
				Component: PlanningPage,
				handle: { title: 'Planning' },
			},
			{
				path: 'data',
				Component: DataPage,
				handle: { title: 'Data' },
			},
		],
	},
]);
