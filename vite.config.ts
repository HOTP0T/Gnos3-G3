import { hostname } from 'node:os';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

import { viteStaticCopy } from 'vite-plugin-static-copy';

export default defineConfig({
	plugins: [
		sveltekit(),
		viteStaticCopy({
			targets: [
				{
					src: 'node_modules/onnxruntime-web/dist/*.jsep.*',

					dest: 'wasm'
				}
			]
		})
	],
	define: {
		APP_VERSION: JSON.stringify(process.env.npm_package_version),
		APP_BUILD_HASH: JSON.stringify(process.env.APP_BUILD_HASH || 'dev-build')
	},
	server: {
		// Vite answers IPs and localhost only; LAN / Tailscale users who open
		// the box by name (`<host>`, `<host>.local`, `<host>.<tailnet>.ts.net`)
		// would get "Blocked request" without this.
		allowedHosts: [hostname().toLowerCase(), '.local', '.ts.net'],
		watch: {
			// The Python venv and the backend's runtime data (vector DB, uploads,
			// SQLite) live inside this tree. Watching them exhausts inotify
			// (ENOSPC crash right after "ready") and contributes nothing to HMR.
			ignored: ['**/venv/**', '**/.venv/**', '**/backend/data/**']
		},
		proxy: {
			'/static': 'http://localhost:8080',
			// The shorthand rewrites Host to localhost:8080; xfwd keeps the browser's
			// host in X-Forwarded-Host, which /auths/k4mi/open uses to send LAN
			// users to K4mi on the address they typed rather than to localhost.
			'/api': { target: 'http://localhost:8080', changeOrigin: true, xfwd: true },
			'/ollama': 'http://localhost:8080',
			'/openai': 'http://localhost:8080',
			'/ws/socket.io': {
				target: 'http://localhost:8080',
				ws: true
			}
		}
	},
	build: {
		sourcemap: true
	},
	worker: {
		format: 'es'
	},
	esbuild: {
		pure: process.env.ENV === 'dev' ? [] : ['console.log', 'console.debug', 'console.error']
	}
});
