import type { LayoutServerLoad } from './$types';
import { BACKEND_URL } from '$lib/server/api.js';

export const load: LayoutServerLoad = async ({ cookies, fetch }) => {
	const token = cookies.get('access_token');
	if (!token) {
		return { loggedIn: false, isAdmin: false };
	}

	try {
		const res = await fetch(`${BACKEND_URL}/is_admin`, {
			headers: { Authorization: `Bearer ${token}` }
		});
		if (!res.ok) {
			return { loggedIn: false, isAdmin: false };
		}
		const isAdmin = await res.json();
		return { loggedIn: true, isAdmin: Boolean(isAdmin) };
	} catch (e) {
		console.error('Failed to check admin status:', e);
		return { loggedIn: true, isAdmin: false };
	}
};
