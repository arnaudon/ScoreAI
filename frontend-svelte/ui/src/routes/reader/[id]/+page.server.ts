import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

const BACKEND_URL = 'http://localhost:8000';

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
				backendUrl: BACKEND_URL 
			};
		}
	} catch (error) {
		console.error('Failed to fetch score:', error);
	}

	return { score: null, token, backendUrl: BACKEND_URL };
};
