import adapter from '@sveltejs/adapter-node';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

// Default matches the previous hardcoded list so prod CSRF keeps working
// if CSRF_TRUSTED_ORIGINS isn't set. The deploy workflow may override it.
const DEFAULT_TRUSTED_ORIGINS = [
	'localhost',
	'127.0.0.1',
	'188.213.128.236',
	'http://188.213.128.236',
	'https://188.213.128.236'
];

const trustedOrigins = process.env.CSRF_TRUSTED_ORIGINS
	? process.env.CSRF_TRUSTED_ORIGINS.split(',')
			.map((o) => o.trim())
			.filter(Boolean)
	: DEFAULT_TRUSTED_ORIGINS;

/** @type {import('@sveltejs/kit').Config} */
const config = {
	preprocess: [vitePreprocess()],
	kit: {
		adapter: adapter(),
		csrf: {
			trustedOrigins
		}
	}
};

export default config;
