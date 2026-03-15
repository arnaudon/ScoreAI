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

	const res = await fetch(`${BACKEND_URL}/user`, {
		headers: { Authorization: `Bearer ${token}` }
	});

	if (!res.ok) {
		cookies.delete('access_token', { path: '/', httpOnly: true, secure: !dev, sameSite: 'lax' });
		redirect(303, '/login');
	}

	const user = await res.json();

	let hasScores = false;
	try {
		const scoresRes = await fetch(`${BACKEND_URL}/scores`, {
			headers: { Authorization: `Bearer ${token}` }
		});
		if (scoresRes.ok) {
			const scores = await scoresRes.json();
			hasScores = Array.isArray(scores) && scores.length > 0;
		}
	} catch (e) {
		console.error('Failed to fetch scores check', e);
	}

	return { user, hasScores };
};

export const actions: Actions = {
	ask: async ({ request, cookies, fetch }) => {
		const token = cookies.get('access_token');
		const data = await request.formData();
		const question = data.get('question');
		const messageHistoryRaw = data.get('message_history');

		if (!question) {
			return fail(400, { error: 'Missing question' });
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
			const scores = scoresRes.ok ? await scoresRes.json() : [];
			const deps = JSON.stringify({ scores });

			const response = await fetch(`${BACKEND_URL}/agent`, {
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

			if (response.ok) {
				const result = await response.json();
				let scoreDetails = null;
				let returnScores = [];
				
				const scoreId = result?.score_id || result?.response?.score_id;
				if (scoreId) {
					scoreDetails = scores.find((s: any) => s.id === scoreId) || null;
				}

				const scoreIds = result?.score_ids || result?.response?.score_ids || [];
				if (Array.isArray(scoreIds) && scoreIds.length > 0) {
					returnScores = scoreIds.map((id: any) => scores.find((s: any) => s.id === id)).filter(Boolean);
				} else if (scoreDetails) {
					returnScores = [scoreDetails];
				}

				return { success: true, answer: result, question: question.toString(), scoreDetails, scores: returnScores };
			} else {
				const result = await response.json().catch(() => ({}));
				return fail(response.status, { error: result.detail || `Failed to get response (${response.status})` });
			}
		} catch (error) {
			console.error('Agent error:', error);
			return fail(500, { error: 'Server error when contacting backend' });
		}
	}
};
