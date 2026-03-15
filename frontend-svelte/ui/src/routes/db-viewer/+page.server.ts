import { fail, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';
import { env } from '$env/dynamic/private';
import { dev } from '$app/environment';

const BACKEND_URL = env.BACKEND_URL || 'http://localhost:8000';

export const load: PageServerLoad = async ({ cookies, fetch }) => {
	const token = cookies.get('access_token');
	if (!token) {
		redirect(303, '/login');
	}

	async function fetchUser() {
		const res = await fetch(`${BACKEND_URL}/user`, {
			headers: { Authorization: `Bearer ${token}` }
		});
		if (!res.ok) {
			cookies.delete('access_token', { path: '/', httpOnly: true, secure: !dev, sameSite: 'lax' });
			redirect(303, '/login');
		}
		return res.json();
	}

	async function fetchScores() {
		const res = await fetch(`${BACKEND_URL}/scores`, {
			headers: {
				Authorization: `Bearer ${token}`
			}
		});
		return res.ok ? await res.json() : [];
	}

	try {
		const [user, scores] = await Promise.all([fetchUser(), fetchScores()]);
		return { user, scores };
	} catch (error) {
		console.error('Failed to fetch page data:', error);
		redirect(303, '/login');
	}
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

			return { success: true, scoreAdded: true };
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
		const question = data.get('question');
		const messageHistoryRaw = data.get('message_history');

		if (!question) {
			return fail(400, { error: 'Missing prompt' });
		}

		let messageHistory = null;
		if (messageHistoryRaw) {
			try {
				messageHistory = JSON.parse(messageHistoryRaw.toString());
			} catch (e) {
				console.error('Failed to parse message_history', e);
			}
		}

		try {
			const scoresRes = await fetch(`${BACKEND_URL}/scores`, {
				headers: {
					Authorization: `Bearer ${token}`
				}
			});
			const scores_deps = scoresRes.ok ? await scoresRes.json() : [];
			const deps = JSON.stringify({ scores: scores_deps });

			const res = await fetch(`${BACKEND_URL}/imslp_agent`, {
				method: 'POST',
				headers: {
					Authorization: `Bearer ${token}`,
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					prompt: question.toString(),
					deps: deps,
					message_history: messageHistory
				})
			});

			if (!res.ok) {
				const result = await res.json().catch(() => ({}));
				return fail(res.status, { error: result.detail || 'Failed to query agent' });
			}

			const json = await res.json();
			let scores = [];
			const score_ids = json.response?.score_ids || [];
			const agent_response_text = json.response?.response || '';

			if (score_ids.length > 0) {
				const idsParam = encodeURIComponent(JSON.stringify(score_ids));
				const scoresRes = await fetch(`${BACKEND_URL}/imslp/scores_by_ids?score_ids=${idsParam}`, {
					headers: { Authorization: `Bearer ${token}` }
				});
				if (scoresRes.ok) {
					scores = await scoresRes.json();
				}
			}

			const returned_message_history = json.response?.message_history || messageHistory;

			return {
				success: true,
				question: question.toString(),
				agent_results: {
					response: agent_response_text,
					scores,
					message_history: returned_message_history
				}
			};
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
		const file = data.get('file') as File;

		if (!imslp_id || !file || file.size === 0) {
			return fail(400, { error: 'Missing IMSLP ID or PDF File' });
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

			// 2. Fetch IMSLP Score Details
			const idsParam = encodeURIComponent(JSON.stringify([Number(imslp_id)]));
			const imslpRes = await fetch(`${BACKEND_URL}/imslp/scores_by_ids?score_ids=${idsParam}`, {
				headers: { Authorization: `Bearer ${token}` }
			});

			if (!imslpRes.ok) {
				return fail(imslpRes.status, { error: 'Failed to fetch IMSLP score' });
			}

			const imslpScores = await imslpRes.json();
			if (!imslpScores || imslpScores.length === 0) {
				return fail(404, { error: 'IMSLP score not found' });
			}

			const imslpScore = imslpScores[0];

			const newScore = {
				title: imslpScore.title,
				composer: imslpScore.composer,
				pdf_path: filename,
				instrumentation: imslpScore.instrumentation || '',
				style: imslpScore.style || '',
				period: imslpScore.period || '',
				year: imslpScore.year && !isNaN(Number(imslpScore.year)) ? Number(imslpScore.year) : null,
				key: imslpScore.key || ''
			};

			const scoreRes = await fetch(`${BACKEND_URL}/scores`, {
				method: 'POST',
				headers: {
					Authorization: `Bearer ${token}`,
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(newScore)
			});

			if (!scoreRes.ok) {
				return fail(scoreRes.status, { error: 'Failed to add score to database' });
			}

			return { success: true, scoreAdded: true };
		} catch (error) {
			console.error('Add IMSLP error:', error);
			return fail(500, { error: 'Server error when contacting backend' });
		}
	},
	recomplete: async ({ request, cookies, fetch }) => {
		const token = cookies.get('access_token');
		if (!token) {
			return fail(401, { error: 'Unauthorized' });
		}

		const data = await request.formData();
		const id = data.get('id');
		const title = data.get('title');
		const composer = data.get('composer');
		const pdf_path = data.get('pdf_path');

		if (!id || !title || !composer) {
			return fail(400, { error: 'Missing required fields' });
		}

		try {
			const initialScoreData = {
				title: title.toString(),
				composer: composer.toString(),
				pdf_path: pdf_path ? pdf_path.toString() : ''
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
			
			if (typeof scoreData === 'string') {
				try {
					scoreData = JSON.parse(scoreData);
				} catch (e) {
					console.error('Could not parse scoreData string');
				}
			}
			
			if (scoreData && typeof scoreData === 'object' && !scoreData.title) {
				if (scoreData.score) scoreData = scoreData.score;
				else if (scoreData.response) scoreData = scoreData.response;
			}
			
			const finalScoreData = {
				...scoreData,
				pdf_path: pdf_path ? pdf_path.toString() : '',
				source: 'manual'
			};

			const updateRes = await fetch(`${BACKEND_URL}/scores/${id}`, {
				method: 'PUT',
				headers: {
					Authorization: `Bearer ${token}`,
					'Content-Type': 'application/json'
				},
				body: JSON.stringify(finalScoreData)
			});

			if (!updateRes.ok) {
				return fail(updateRes.status, { error: 'Failed to update score' });
			}

			return { success: true };
		} catch (error) {
			console.error('Recomplete error:', error);
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
