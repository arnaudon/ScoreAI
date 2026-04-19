/**
 * TypeScript mirrors of the Python response/table models in `shared/shared/`.
 * Hand-maintained subset covering what the Svelte app actually consumes; if
 * the backend schema diverges, update both sides together.
 */

export type Difficulty = 'easy' | 'moderate' | 'intermediate' | 'advanced' | 'expert';

export type Period =
	| 'Medieval'
	| 'Renaissance'
	| 'Baroque'
	| 'Classical'
	| 'Romantic'
	| 'Modernist'
	| 'Postmodernist';

/** Matches `shared.scores.Score`. */
export interface Score {
	id: number;
	title: string;
	composer: string;
	year: number;
	period: Period;
	genre: string;
	form: string;
	style: string;
	key: string;
	instrumentation: string;
	pdf_path: string;
	number_of_plays: number;
	source: string;
	imslp_id: number | null;
	user_id: number | null;
	short_description: string;
	short_description_fr: string;
	long_description: string;
	long_description_fr: string;
	youtube_url: string;
	difficulty: Difficulty;
	notable_interpreters: string;
}

/** Matches `shared.scores.IMSLP`. */
export interface IMSLPScore {
	id: number;
	title: string;
	composer: string;
	year: number | string;
	period: string;
	genre: string;
	form: string;
	style: string;
	key: string;
	instrumentation: string;
	permlink: string;
	score_metadata: string;
	pdf_urls: string;
}

/** Matches `shared.user.User` (subset exposed via `/user`). Password is never returned. */
export interface User {
	id: number;
	username: string;
	email: string | null;
	first_name: string | null;
	last_name: string | null;
	instrument: string | null;
	role: string;
	credits: number;
	max_credits: number;
	last_login: string | null;
}

/** Admin `/users` includes a denormalized score count. */
export interface AdminUser extends User {
	score_count: number;
}

/** Matches `shared.responses.Response`. */
export interface AgentResponse {
	response: string;
	score_id?: number | null;
	score_ids?: number[] | null;
}

/** Matches `shared.responses.ImslpResponse`. */
export interface ImslpAgentResponse {
	response: string;
	score_ids: number[];
}

/** Wire shape of `FullResponse` / `ImslpFullResponse`. */
export interface FullAgentResponse<T = AgentResponse> {
	response: T;
	message_history: unknown[];
}

export interface ImslpStats {
	total_works: number;
	total_composers: number;
}

export interface ImslpProgress {
	status: string;
	page: number;
	total?: number;
	cancel_requested?: boolean;
}

export interface ActiveModels {
	main: string;
	imslp: string;
	complete: string;
	imslp_complete: string;
}
