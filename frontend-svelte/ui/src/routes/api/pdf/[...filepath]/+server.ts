import type { RequestHandler } from './$types';
import { env } from '$env/dynamic/private';

const BACKEND_URL = env.BACKEND_URL || 'http://localhost:8000';

export const GET: RequestHandler = async ({ params, url, fetch }) => {
	const filename = params.filepath;
	const token = url.searchParams.get('token');

	if (!filename || !token) {
		return new Response('Not found', { status: 404 });
	}

	const backendPdfUrl = `${BACKEND_URL}/pdf/${filename}?token=${token}`;

	try {
		const response = await fetch(backendPdfUrl);

		if (!response.ok) {
			return new Response(response.body, {
				status: response.status,
				statusText: response.statusText,
				headers: {
					'Content-Type': response.headers.get('Content-Type') || 'application/json'
				}
			});
		}

		const headers = new Headers();
		headers.set('Content-Type', 'application/pdf');
		if (response.headers.has('Content-Length')) {
			headers.set('Content-Length', response.headers.get('Content-Length')!);
		}
		if (response.headers.has('Cache-Control')) {
			headers.set('Cache-Control', response.headers.get('Cache-Control')!);
		}

		return new Response(response.body, {
			status: 200,
			headers: headers
		});
	} catch (error) {
		console.error('PDF proxy error:', error);
		return new Response('Internal Server Error', { status: 500 });
	}
};
