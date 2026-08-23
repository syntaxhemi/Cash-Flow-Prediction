import type { ReactNode } from 'react';

type PageLayoutProps = {
	title: string;
	children?: ReactNode;
};

function PageLayout({ title, children }: PageLayoutProps) {
	return (
		<main
			className="mx-auto min-h-svh w-full max-w-360 px-6 pb-24 pt-12 sm:px-10 lg:px-14 lg:pt-10"
			aria-labelledby={`${title.toLowerCase()}-page-title`}
		>
			<h1 id={`${title.toLowerCase()}-page-title`} className="sr-only">
				{title}
			</h1>
			{children}
		</main>
	);
}

export default PageLayout;
