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
	server: {
		proxy: {
			'/api/chat/completions': {
				target: 'http://localhost:8080',
				changeOrigin: true,
				secure: false
			},
			'/api/v1/chat/completions': {
				target: 'http://localhost:8080',
				changeOrigin: true,
				secure: false
			},
			'/api/tradeberg/chat/completions': {
				target: 'http://localhost:8080',
				changeOrigin: true,
				secure: false
			},
			'/api/tradeberg/enhanced-chat': {
				target: 'http://localhost:8080',
				changeOrigin: true,
				secure: false
			},
			'/api': {
				target: 'http://localhost:8080',
				changeOrigin: true,
				secure: false
			}
		}
	},
	define: {
		APP_VERSION: JSON.stringify(process.env.npm_package_version),
		APP_BUILD_HASH: JSON.stringify(process.env.APP_BUILD_HASH || 'dev-build')
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
