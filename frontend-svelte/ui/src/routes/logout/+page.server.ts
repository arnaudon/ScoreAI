import { redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { dev } from '$app/environment';

export const load: PageServerLoad = async ({ cookies }) => {
	cookies.delete('access_token', { path: '/', httpOnly: true, secure: !dev, sameSite: 'lax' });
	redirect(303, '/login');
};

export const actions: Actions = {
	default: async ({ cookies }) => {
		cookies.delete('access_token', { path: '/', httpOnly: true, secure: !dev, sameSite: 'lax' });
		redirect(303, '/login');
	}
};
