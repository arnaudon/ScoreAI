import { env } from '$env/dynamic/private';

/** Backend base URL used by all server-side loaders and actions. */
export const BACKEND_URL = env.BACKEND_URL || 'http://localhost:8000';
