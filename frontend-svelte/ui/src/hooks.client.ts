import { env } from '$env/dynamic/public';
import type { HandleClientError } from '@sveltejs/kit';
import * as Sentry from '@sentry/sveltekit';

if (env.PUBLIC_SENTRY_DSN) {
	Sentry.init({
		dsn: env.PUBLIC_SENTRY_DSN,
		environment: env.PUBLIC_SENTRY_ENVIRONMENT ?? 'production',
		tracesSampleRate: Number(env.PUBLIC_SENTRY_TRACES_SAMPLE_RATE ?? '0.1')
	});
}

export const handleError: HandleClientError = Sentry.handleErrorWithSentry();
