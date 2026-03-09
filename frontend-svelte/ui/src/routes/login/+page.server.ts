import { fail, redirect } from '@sveltejs/kit';
import type { Actions } from './$types';
import { dev } from '$app/environment';

const BACKEND_URL = 'http://localhost:8000';

export const actions: Actions = {
	default: async ({ request, cookies, fetch }) => {
		const data = await request.formData();
		const username = data.get('username');
		const password = data.get('password');

		if (!username || !password) {
			return fail(400, { username, error: 'Missing username or password' });
		}

		const body = new URLSearchParams();
		body.append('username', username.toString());
		body.append('password', password.toString());

		const response = await fetch(`${BACKEND_URL}/token`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/x-www-form-urlencoded'
			},
			body: body
		});

		if (!response.ok) {
			const result = await response.json();
			return fail(response.status, { username, error: result.detail || 'Login failed' });
		}

		const tokenData = await response.json();

		cookies.set('access_token', tokenData.access_token, {
			path: '/',
			httpOnly: true,
			secure: !dev,
			sameSite: 'strict',
			maxAge: 60 * 60 * 24 // 1 day
		});

		redirect(303, '/');
	}
};
