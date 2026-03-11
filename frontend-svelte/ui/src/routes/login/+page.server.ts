import { fail, redirect } from '@sveltejs/kit';
import type { Actions } from './$types';
import { dev } from '$app/environment';
import { env } from '$env/dynamic/private';

const BACKEND_URL = env.BACKEND_URL || 'http://localhost:8000';

export const actions: Actions = {
	login: async ({ request, cookies, fetch }) => {
		const data = await request.formData();
		const username = data.get('username');
		const password = data.get('password');

		if (!username || !password) {
			return fail(400, { username: username?.toString(), error: 'Missing username or password' });
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
			return fail(response.status, { username: username.toString(), error: result.detail || 'Login failed' });
		}

		const tokenData = await response.json();

		cookies.set('access_token', tokenData.access_token, {
			path: '/',
			httpOnly: true,
			secure: !dev,
			sameSite: 'strict',
			maxAge: 60 * 60 * 24 // 1 day
		});

		redirect(303, '/success');
	},

	register: async ({ request, cookies, fetch }) => {
		const data = await request.formData();
		const username = data.get('username');
		const password = data.get('password');

		if (!username || !password) {
			return fail(400, { username: username?.toString(), error: 'Missing username or password' });
		}

		const response = await fetch(`${BACKEND_URL}/users`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				username: username.toString(),
				password: password.toString()
			})
		});

		if (!response.ok) {
			let errorMsg = 'Registration failed';
			try {
				const result = await response.json();
				errorMsg = result.detail || errorMsg;
			} catch (e) {}
			return fail(response.status, { username: username.toString(), error: errorMsg });
		}

		// Automatically log in the user after successful registration
		const body = new URLSearchParams();
		body.append('username', username.toString());
		body.append('password', password.toString());

		const loginRes = await fetch(`${BACKEND_URL}/token`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/x-www-form-urlencoded'
			},
			body: body
		});

		if (loginRes.ok) {
			const tokenData = await loginRes.json();
			cookies.set('access_token', tokenData.access_token, {
				path: '/',
				httpOnly: true,
				secure: !dev,
				sameSite: 'strict',
				maxAge: 60 * 60 * 24 // 1 day
			});
			redirect(303, '/success');
		} else {
			return { username: username.toString(), success: true, message: 'Registration successful! Please log in.' };
		}
	}
};
