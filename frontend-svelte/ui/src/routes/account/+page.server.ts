import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = async ({ cookies }) => {
	const token = cookies.get('access_token');
	
	if (!token) {
		redirect(303, '/login');
	}
	
	return {};
};
