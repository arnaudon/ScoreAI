import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { env } from '$env/dynamic/private';
import { env as publicEnv } from '$env/dynamic/public';

const BACKEND_URL = env.BACKEND_URL || 'http://localhost:8000';
const PUBLIC_BACKEND_URL = publicEnv.PUBLIC_BACKEND_URL || 'http://localhost:8000';

export const load: PageServerLoad = async ({ cookies, params, fetch }) => {
	const token = cookies.get('access_token');
	if (!token) {
		redirect(303, '/login');
	}

	try {
		const response = await fetch(`${BACKEND_URL}/scores`, {
			headers: {
				Authorization: `Bearer ${token}`
			}
		});

		if (response.ok) {
			const scores = await response.json();
			const score = scores.find((s: any) => s.id === Number(params.id));
			
			if (score) {
				cookies.set('last_score_id', params.id, { path: '/' });
			}

			return { 
				score, 
				token, 
				publicBackendUrl: PUBLIC_BACKEND_URL 
			};
		}
	} catch (error) {
		console.error('Failed to fetch score:', error);
	}

	return { score: null, token, publicBackendUrl: PUBLIC_BACKEND_URL };
};
