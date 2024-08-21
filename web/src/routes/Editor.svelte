<script lang="ts">
	import CodeMirror from 'svelte-codemirror-editor';
	import { python } from '@codemirror/lang-python';
	import { githubLight, githubDark } from '@uiw/codemirror-theme-github';
	import { files, exp } from '$lib/index';

	let value = $files[$exp.tabs[$exp.current_tab]].content;
	let font = 'Jetbrains Mono';
	const settings = {
        '&': {
            height: 'calc(100vh - var(--tab-height) - .3rem + var(--border-width) - calc(var(--tab-icon-gap) / 2) - 2.1rem)',
        },
        '.cm-scroller': {scrollbarWidth: "thin"},
		'.cm-content': {
			fontFamily: `${font}, monospace`,
			fontSize: '.78rem'
		},
		'.cm-gutter': {
			fontFamily: `${font}, monospace`,
			fontSize: '.78rem'
		}
	};

    
</script>

<CodeMirror bind:value lang={python()} extensions={[githubLight]} styles={settings} />
