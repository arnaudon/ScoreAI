import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { env } from '$env/dynamic/private';

const BACKEND_URL = env.BACKEND_URL || 'http://localhost:8000';

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

			// 2. Complete Score Data using the Agent
			const initialScoreData = {
				title: title.toString(),
				composer: composer.toString(),
				pdf_path: filename
			};

			const completeRes = await fetch(`${BACKEND_URL}/complete_score`, {
				method: 'POST',
				headers: {
					Authorization: `Bearer ${token}`,
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(initialScoreData)
			});

			if (!completeRes.ok) {
				return fail(completeRes.status, { error: 'Failed to complete score data with agent' });
			}

			let scoreData = await completeRes.json();
			
			// Handle case where agent returns a JSON string instead of an object
			if (typeof scoreData === 'string') {
				try {
					scoreData = JSON.parse(scoreData);
				} catch (e) {
					console.error('Could not parse scoreData string');
				}
			}
			
			// Handle case where agent wraps the score in a response object
			if (scoreData && typeof scoreData === 'object' && !scoreData.title) {
				if (scoreData.score) scoreData = scoreData.score;
				else if (scoreData.response) scoreData = scoreData.response;
			}
			
			// Create the final payload, ensuring pdf_path and source are explicitly set
			const finalScoreData = {
				...scoreData,
				pdf_path: filename,
				source: 'manual'
			};

			// 3. Add Score to DB
			const scoreRes = await fetch(`${BACKEND_URL}/scores`, {
				method: 'POST',
				headers: {
					Authorization: `Bearer ${token}`,
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(finalScoreData)
			});

			if (!scoreRes.ok) {
				return fail(scoreRes.status, { error: 'Failed to save score' });
			}

			return { success: true };
		} catch (error) {
			console.error('Upload error:', error);
			return fail(500, { error: 'Server error when contacting backend' });
		}
	},
	ask_agent: async ({ request, cookies, fetch }) => {
		const token = cookies.get('access_token');
		if (!token) {
			return fail(401, { error: 'Unauthorized' });
		}

		const data = await request.formData();
		const prompt = data.get('prompt');

		if (!prompt) {
			return fail(400, { error: 'Missing prompt' });
		}

		try {
			const res = await fetch(`${BACKEND_URL}/agent/imslp`, {
				method: 'POST',
				headers: {
					Authorization: `Bearer ${token}`,
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ prompt: prompt.toString() })
			});

			if (!res.ok) {
				return fail(res.status, { error: 'Failed to query agent' });
			}

			const agent_results = await res.json();
			let scores = agent_results.scores || [];
			
			// If the agent returned score_ids but no detailed score objects, fetch the details
			if (agent_results.score_ids && agent_results.score_ids.length > 0 && scores.length === 0) {
				const idsParam = encodeURIComponent(JSON.stringify(agent_results.score_ids));
				const scoresRes = await fetch(`${BACKEND_URL}/imslp/scores_by_ids?score_ids=${idsParam}`, {
					headers: { Authorization: `Bearer ${token}` }
				});
				if (scoresRes.ok) {
					scores = await scoresRes.json();
				}
			}
			
			agent_results.scores = scores;

			return { success: true, agent_results };
		} catch (error) {
			console.error('Ask agent error:', error);
			return fail(500, { error: 'Server error when contacting backend' });
		}
	},
	add_imslp: async ({ request, cookies, fetch }) => {
		const token = cookies.get('access_token');
		if (!token) {
			return fail(401, { error: 'Unauthorized' });
		}

		const data = await request.formData();
		const imslp_id = data.get('imslp_id');

		if (!imslp_id) {
			return fail(400, { error: 'Missing IMSLP ID' });
		}

		try {
			// Assuming backend has a specific endpoint to pull from IMSLP. 
			// Adjust the URL as needed if your backend route differs.
			const res = await fetch(`${BACKEND_URL}/scores/imslp/${imslp_id}`, {
				method: 'POST',
				headers: {
					Authorization: `Bearer ${token}`
				}
			});

			if (!res.ok) {
				return fail(res.status, { error: 'Failed to add score from IMSLP' });
			}

			return { success: true };
		} catch (error) {
			console.error('Add IMSLP error:', error);
			return fail(500, { error: 'Server error when contacting backend' });
		}
	},
	delete: async ({ request, cookies, fetch }) => {
		const token = cookies.get('access_token');
		if (!token) {
			return fail(401, { error: 'Unauthorized' });
		}

		const data = await request.formData();
		const id = data.get('id');

		if (!id) {
			return fail(400, { error: 'Missing score ID' });
		}

		try {
			const res = await fetch(`${BACKEND_URL}/scores/${id}`, {
				method: 'DELETE',
				headers: {
					Authorization: `Bearer ${token}`
				}
			});

			if (!res.ok) {
				return fail(res.status, { error: 'Failed to delete score' });
			}

			return { success: true };
		} catch (error) {
			console.error('Delete error:', error);
			return fail(500, { error: 'Server error when contacting backend' });
		}
	}
};
