# Svelte frontend

SvelteKit 5 app using Tailwind 4, shadcn-svelte, and Paraglide i18n (en/fr). Adapter: `@sveltejs/adapter-node`. This is the production UI served at [scoreguide.ch](https://scoreguide.ch).

## Layout

- `src/routes/` — pages and `+page.server.ts` loaders that proxy to the FastAPI backend.
- `src/lib/server/api.ts` — shared `BACKEND_URL`; import this instead of redeclaring the env var.
- `src/lib/components/` — shadcn primitives plus app-specific components (`AgentChat`, `Sidebar`).
- `messages/en.json`, `messages/fr.json` — Paraglide catalogs. The generated `src/lib/paraglide/` is produced by `vite build` / `vite dev` via the paraglide plugin.
- `e2e/` — reserved for future Playwright suites (not in CI yet).

## Auth / backend wiring

Cookies hold the JWT (`access_token`, httpOnly + secure + sameSite=lax). The root `+layout.server.ts` asks the backend `/is_admin` on each SSR instead of decoding the JWT client-side — the backend re-verifies on every call, so this is the single source of truth.

Server-side fetches use `BACKEND_URL`; browser fetches use `PUBLIC_BACKEND_URL` (only `reader/[id]` currently exposes the latter).

## Commands

```bash
npm ci
npm run dev              # vite dev on :3000
npm run build            # production SSR bundle + paraglide codegen
node build               # run the production bundle locally
npm run check            # svelte-check (pre-existing paraglide/any-typed noise)
npm run lint             # prettier + eslint (pre-existing formatting noise)
npm run test:unit        # vitest (node + chromium projects)
npm run test:e2e         # playwright
```

CI (`.github/workflows/frontend.yml`) gates on `npm run build` + `vitest --project server`. `check` and `lint` run with `continue-on-error` until the pre-existing backlog is cleaned up.
