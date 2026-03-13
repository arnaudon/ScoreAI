import { fail, redirect } from '@sveltejs/kit';
import type { Actions } from './$types';
import { env } from '$env/dynamic/private';

const BACKEND_URL = env.BACKEND_URL || 'http://localhost:8000';

export const actions: Actions = {
	login: async ({ request, cookies, fetch }) => {
		const data = await request.formData();
		const username = data.get('username');
		const password = data.get('password');
		const remember = data.get('remember');

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

		const maxAge = remember === 'on' ? 60 * 60 * 24 * 30 : 60 * 60 * 24; // 30 days or 1 day

		cookies.set('access_token', tokenData.access_token, {
			path: '/',
			httpOnly: true,
			secure: false,
			sameSite: 'strict',
			maxAge
		});

		redirect(303, '/success');
	},

	register: async ({ request, cookies, fetch }) => {
		const data = await request.formData();
		const username = data.get('username');
		const password = data.get('password');
		const email = data.get('email');
		const instrument = data.get('instrument');

		if (!username || !password || !email) {
			return fail(400, {
				username: username?.toString(),
				email: email?.toString(),
				instrument: instrument?.toString(),
				error: 'Missing username, password or email'
			});
		}

		const response = await fetch(`${BACKEND_URL}/users`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				username: username.toString(),
				password: password.toString(),
				email: email.toString(),
				instrument: instrument?.toString()
			})
		});

		if (!response.ok) {
			let errorMsg = 'Registration failed';
			try {
				const result = await response.json();
				errorMsg = result.detail || errorMsg;
			} catch (e) {}
			return fail(response.status, {
				username: username.toString(),
				email: email.toString(),
				instrument: instrument?.toString(),
				error: errorMsg
			});
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
				secure: false,
				sameSite: 'strict',
				maxAge: 60 * 60 * 24 // 1 day
			});
			redirect(303, '/success');
		} else {
			return { username: username.toString(), success: true, message: 'Registration successful! Please log in.' };
		}
	}
};
