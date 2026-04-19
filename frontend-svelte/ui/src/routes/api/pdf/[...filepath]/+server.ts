import type { RequestHandler } from './$types';
import { BACKEND_URL } from '$lib/server/api.js';

export const GET: RequestHandler = async ({ params, url, fetch }) => {
	const pathWithQuery = params.filepath;
	let filename = pathWithQuery;
	let token: string | null = null;

	// The `file` parameter passed to PDF.js viewer is a URL that gets encoded.
	// This means our query parameter `?token=...` becomes part of the path.
	// SvelteKit decodes it, so we can parse it from the `filepath` parameter.
	const tokenMarker = '?token=';
	const tokenIndex = pathWithQuery.indexOf(tokenMarker);

	if (tokenIndex !== -1) {
		filename = pathWithQuery.substring(0, tokenIndex);
		token = pathWithQuery.substring(tokenIndex + tokenMarker.length);
	} else {
		token = url.searchParams.get('token');
	}

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
