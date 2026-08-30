import { RouterProvider } from 'react-router-dom';
import { router } from '@/app/router';
import { EnterpriseProvider } from '@/providers/EnterpriseProvider';

function App() {
	return (
		<EnterpriseProvider>
			<RouterProvider router={router} />
		</EnterpriseProvider>
	);
}

export default App;
