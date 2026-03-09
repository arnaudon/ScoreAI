import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';

const BACKEND_URL = 'http://localhost:8000';

export const load: PageServerLoad = async ({ cookies, fetch }) => {
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
			return { scores };
		}
	} catch (error) {
		console.error('Failed to fetch scores:', error);
	}

	return { scores: [] };
};

export const actions: Actions = {
	upload: async ({ request, cookies, fetch }) => {
		const token = cookies.get('access_token');
		if (!token) {
			return fail(401, { error: 'Unauthorized' });
		}

		const data = await request.formData();
		const title = data.get('title');
		const composer = data.get('composer');
		const file = data.get('file') as File;

		if (!title || !composer || !file || file.size === 0) {
			return fail(400, { error: 'Missing required fields' });
		}

		try {
			// 1. Upload PDF
			let uploadFilename = file.name;
			if (!uploadFilename.toLowerCase().endsWith('.pdf')) {
				uploadFilename += '.pdf';
			}

			const formData = new FormData();
			formData.append('file', file, uploadFilename);
			const uploadRes = await fetch(`${BACKEND_URL}/pdf`, {
				method: 'POST',
				headers: {
					Authorization: `Bearer ${token}`
				},
				body: formData
			});

			if (!uploadRes.ok) {
				return fail(uploadRes.status, { error: 'Failed to upload PDF' });
			}

			const uploadData = await uploadRes.json();
			const filename = uploadData.file_id || uploadFilename;

			// 2. Add Score to DB
			const scoreData = {
				title: title.toString(),
				composer: composer.toString(),
				filename: filename
			};

			const scoreRes = await fetch(`${BACKEND_URL}/scores`, {
				method: 'POST',
				headers: {
					Authorization: `Bearer ${token}`,
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(scoreData)
			});

			if (!scoreRes.ok) {
				return fail(scoreRes.status, { error: 'Failed to save score' });
			}

			return { success: true };
		} catch (error) {
			console.error('Upload error:', error);
			return fail(500, { error: 'Server error when contacting backend' });
		}
	}
};
