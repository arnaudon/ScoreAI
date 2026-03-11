import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { env } from '$env/dynamic/private';

const BACKEND_URL = env.BACKEND_URL || 'http://localhost:8000';

export const load: PageServerLoad = async ({ cookies, fetch }) => {
	const token = cookies.get('access_token');
	
	if (!token) {
		redirect(303, '/login');
	}

	try {
		const payloadBase64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
		const payload = JSON.parse(atob(payloadBase64));
		if (payload.role !== 'admin' && payload.is_admin !== true) {
			redirect(303, '/');
		}

		const response = await fetch(`${BACKEND_URL}/users`, {
			headers: {
				Authorization: `Bearer ${token}`
			}
		});

		let users = [];
		if (response.ok) {
			users = await response.json();
		}

		let stats = { total_works: 0, total_composers: 0 };
		const statsResponse = await fetch(`${BACKEND_URL}/imslp/stats`, {
			headers: { Authorization: `Bearer ${token}` }
		});
		if (statsResponse.ok) {
			stats = await statsResponse.json();
		}

		let progress = { status: 'idle', page: 0, total: 0 };
		const progressResponse = await fetch(`${BACKEND_URL}/imslp/progress`, {
			method: 'POST',
			headers: { Authorization: `Bearer ${token}` }
		});
		if (progressResponse.ok) {
			progress = await progressResponse.json();
		}

		return { users, stats, progress };
	} catch (error) {
		console.error('Failed to fetch admin data:', error);
	}

	return { users: [], stats: { total_works: 0, total_composers: 0 }, progress: { status: 'idle', page: 0, total: 0 } };
};

export const actions = {
	update: async ({ request, cookies, fetch }) => {
		const data = await request.formData();
		const maxPages = data.get('max_pages') || '300';
		const token = cookies.get('access_token');
		await fetch(`${BACKEND_URL}/imslp/start/${maxPages}`, {
			method: 'POST',
			headers: { Authorization: `Bearer ${token}` }
		});
	},
	empty: async ({ cookies, fetch }) => {
		const token = cookies.get('access_token');
		await fetch(`${BACKEND_URL}/imslp/empty`, {
			method: 'POST',
			headers: { Authorization: `Bearer ${token}` }
		});
	},
	cancel: async ({ cookies, fetch }) => {
		const token = cookies.get('access_token');
		await fetch(`${BACKEND_URL}/imslp/cancel`, {
			method: 'POST',
			headers: { Authorization: `Bearer ${token}` }
		});
	}
};
