import { hostname } from 'node:os';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import { resolveBuildInfo } from './scripts/build-info.js';

import { viteStaticCopy } from 'vite-plugin-static-copy';

const backendTarget = process.env.WEBUI_BACKEND_URL || 'http://localhost:8080';
const buildInfo = resolveBuildInfo();

export default defineConfig({
	resolve: {
		conditions: ['onnxruntime-web-use-extern-wasm']
	},
	plugins: [
		sveltekit(),
		viteStaticCopy({
			targets: [
				{
					src: 'src/lib/encryption/vendor/THIRD_PARTY_LICENSES.txt',
					dest: 'licenses/encryption'
				},
				{
					src: ['node_modules/@novnc/novnc/docs/LICENSE*', 'node_modules/@novnc/novnc/AUTHORS'],
					dest: 'licenses/novnc'
				},
				{
					src: 'node_modules/onnxruntime-web/dist/*.jsep.*',

					dest: 'wasm'
				}
			]
		})
	],
	define: {
		APP_VERSION: JSON.stringify(process.env.npm_package_version),
		APP_BUILD_HASH: JSON.stringify(buildInfo.hash),
		APP_BUILD_CHANNEL: JSON.stringify(buildInfo.channel)
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
		target: 'es2022',
		sourcemap: true
	},
	optimizeDeps: {
		esbuildOptions: { target: 'es2022' }
	},
	server: {
		proxy: {
			'/api': {
				target: backendTarget,
				changeOrigin: true,
				ws: true
			},
			'/ollama': {
				target: backendTarget,
				changeOrigin: true
			},
			'/openai': {
				target: backendTarget,
				changeOrigin: true
			},
			'/oauth': {
				target: backendTarget,
				changeOrigin: true
			},
			'/ws': {
				target: backendTarget,
				changeOrigin: true,
				ws: true
			}
		}
	},
	worker: {
		format: 'es'
	},
	esbuild: {
		pure: process.env.ENV === 'dev' ? [] : ['console.log', 'console.debug', 'console.error']
	}
});
