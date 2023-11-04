import App from './routes/App.svelte';

const app = new App({
	target: document.body,
	props: {
		name: 'pep8plus'
	}
});

export default app;