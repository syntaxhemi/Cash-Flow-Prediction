import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import '@fontsource-variable/instrument-sans/wght.css';
import '@fontsource-variable/newsreader/wght.css';
import '@fontsource/ibm-plex-mono';
import '@/index.css';
import App from '@/App';

const rootElement = document.getElementById('root');

if (!rootElement) {
	throw new Error('The dashboard root element was not found.');
}

createRoot(rootElement).render(
	<StrictMode>
		<App />
	</StrictMode>,
);
