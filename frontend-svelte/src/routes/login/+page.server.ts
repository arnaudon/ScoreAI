import { fail } from '@sveltejs/kit';
import type { Actions } from './$types';

export const actions: Actions = {
	default: async ({ request }) => {
		const data = await request.formData();
		const email = data.get('email');
		const password = data.get('password');

		if (!email || !password) {
			return fail(400, { email, error: 'Missing email or password' });
		}

		// TODO: Validate credentials
		console.log('Login attempt:', { email, password });

		return fail(401, { email, error: 'Invalid credentials' });
	}
};
