<script lang="ts">
	import { files, exp } from '$lib/index';
	import CodeMirror from 'svelte-codemirror-editor';
	import { python } from '@codemirror/lang-python';
	import { githubLight, githubDark } from '@uiw/codemirror-theme-github';
	import { onMount } from 'svelte';

	let side_width = 3;
	let left_width = 26;
	let right_width = 32;
	let main_width = 100 - side_width - right_width;
	let main_displace = side_width;
	let editor;
	let theme = 'light_mode';

	let selected_error = 0;
	const api = 'http://127.0.0.1:5000';
	const linters = ['pylint', 'flake8', 'ruff'];
	let url;
	let linter;

	let fileSizeDisplay = '0';
	let lineCount = '0';
	let pyVersion = `3.10.11`;

	function fileSize() {
		var sizeInBytes = new Blob([value]).size;
		fileSizeDisplay = (sizeInBytes / 1024).toFixed(2).toString();
		lineCount = value.split('\n').length.toString();
	}

	onMount(() => {
		url = new URL(window.location.toString()).searchParams;
		linter = 'all';

		if (url.has('ruff')) {
			linter = 'ruff';
		} else if (url.has('flake8')) {
			linter = 'flake8';
		} else if (url.has('pylint')) {
			linter = 'pylint';
		}

		if (linter == 'all') {
			linter = 'flake8';
			loadSettings('all');
		} else {
			loadSettings(url.get(linter));
		}
	});

	let link = '';
	let settings;
	let disabled = [];
	let rulecount = 0;
	let ruletotal = 0;

	let activeTab = 'folder';
	let categorisedDisabled = {};

	const nav_buttons = ['folder', 'settings'];
	const side_nav_buttons = ['content_copy', 'download', 'open_in_new'];
	const workspace_left_buttons = ['undo', 'redo'];

	let url_copied = false;

	let value = $files[$exp.tabs[$exp.current_tab]].content;
	let font = 'Jetbrains Mono';
	const editor_settings = {
		'&': {
			height: 'calc(96.5vh - var(--tab-height) - .3rem + var(--border-width) - 1.75rem - 0.51rem)'
		},
		'.cm-scroller': { scrollbarWidth: 'thin' },
		'.cm-content': {
			fontFamily: `${font}, monospace`,
			fontSize: '.78rem'
		},
		'.cm-gutter': {
			fontFamily: `${font}, monospace`,
			fontSize: '.78rem'
		},
		'.cm-gutterElement': {
			minWidth: '3rem !important'
		},
		'.cm-foldGutter': {
			width: '.75rem !important'
		}
	};

	let timer: number;
	let spin = false;
	function watchVariable() {
		if (timer) clearTimeout(timer);
		spin = true;
		timer = setTimeout(handleVariableChange, 4000);
	}

	function handleVariableChange() {
		submit();
		spin = false;
	}

	$: value, watchVariable();
	$: value, fileSize();

	function ruleCount() {
		rulecount = 0;
		ruletotal = 0;
		for (let i in settings) {
			let value = settings[i]['value'];
			if (value) {
				rulecount++;
			}
			ruletotal++;
		}
	}

	let left_expand = true;
	function expand(side: string = 'left') {
		if (side == 'left') {
			if (main_width == 100 - left_width - side_width - right_width) {
				left_expand = true;
				main_width += left_width;
				main_displace -= left_width;
			} else {
				left_expand = false;
				main_width -= left_width;
				main_displace += left_width;
			}
		}
	}

	function removeTabAtIndex(index) {
		if ($exp.tabs.length > 1) {
			exp.update((state) => {
				const newTabs = [...state.tabs];
				newTabs.splice(index, 1);
				if (state.current_tab == state.tabs.length - 1) {
					return { ...state, tabs: newTabs, current_tab: state.current_tab - 1 };
				} else {
					return { ...state, tabs: newTabs };
				}
			});
		}
	}

	function updateTab(number) {
		// Update the 'tabs' array
		const updatedTabs = [...$exp.tabs];
		updatedTabs[$exp.current_tab] = number;

		// Update the state with the modified 'tabs' array
		files.update((file) => {
			const updatedFile = { ...file };
			// Assuming 'number' is the index to be updated
			const numero = $exp.tabs[$exp.current_tab];
			updatedFile[numero] = { title: file[numero].title, content: value }; // Assuming 'value' is defined elsewhere
			return updatedFile;
		});

		exp.update((state) => ({ ...state, tabs: updatedTabs }));
		value = $files[number].content;
	}

	function checkFilenames(name = 'Untitled') {
		let index = 0;
		let array = Object.values($files).map((value) => value['title']);
		while (array.includes(index ? name + ` (${index})` : name)) {
			index += 1;
		}
		return index ? name + ` (${index})` : name;
	}

	function switchTabs(index) {
		// Create a copy of the current tab's contents with updated content
		let updatedContents = {
			...$files[$exp.current_tab],
			content: value
		};

		// Update the contents in the files store
		files.update((store) => ({
			...store,
			[$exp.current_tab]: updatedContents
		}));

		// Update the current tab index
		exp.update((store) => ({ ...store, current_tab: index }));

		// Set the value to the content of the new tab
		value = $files[index].content;
	}

	function copyCode() {
		navigator.clipboard.writeText(value);
	}

	function rawCode() {
		var blob = new Blob([value], { type: 'text/plain' });
		var url = URL.createObjectURL(blob);
		window.open(url);
	}

	function downloadCode() {
		var blob = new Blob([value], { type: 'text/plain' });

		var a = document.createElement('a');
		a.href = URL.createObjectURL(blob);
		let title = $files[$exp.tabs[$exp.current_tab]].title;
		a.download = title.endsWith('.py') ? title : title + '.py';

		document.body.appendChild(a);
		a.click();
		document.body.removeChild(a);
	}

	function toggleCheckbox(value, code, category) {
		if (value) {
			disabled.push(code);
			categorisedDisabled[category].items.push(code);
			settings[code].value = false;
			disabled = [...new Set(disabled)];
			console.log(disabled);
		} else {
			// Remove the ID from the array
			const index = disabled.indexOf(code);
			if (index !== -1) {
				disabled.splice(index, 1);
			}

			const ndex = categorisedDisabled[category].items.indexOf(code);
			if (ndex !== -1) {
				categorisedDisabled[category].items.splice(ndex, 1);
			}
			settings[code].value = true;
		}
		console.log(disabled);
	}

	function superToggle(cat_type, category) {
		if (cat_type === 'none') {
			categorisedDisabled[category].trues.forEach((e) => {
				toggleCheckbox(false, e, category);
			});
			categorisedDisabled[category].items = [];
		} else {
			categorisedDisabled[category].trues.forEach((e) => {
				toggleCheckbox(true, e, category);
			});
			categorisedDisabled[category].items = [...new Set(categorisedDisabled[category].items)];
		}
		console.log(categorisedDisabled[category]);
	}

	function autofix() {
		fetch(`${api}/autofix`, {
			method: 'POST',
			body: JSON.stringify({
				code: value
			}),
			headers: {
				'Content-type': 'application/json',
				Accept: 'application/json'
			}
		})
			.then(function (res) {
				if (!res.ok) {
					throw new Error(res.statusText);
				}
				return res.json();
			})
			.then(function (data) {
				value = data['code'];
			});
	}

	function submit() {
		fetch(`${api}/check`, {
			method: 'POST',
			body: JSON.stringify({
				code: value,
				disable: disabled,
				linter: linter
			}),
			headers: {
				'Content-type': 'application/json',
				Accept: 'application/json'
			}
		})
			.then(function (res) {
				if (!res.ok) {
					throw new Error(res.statusText);
				}
				return res.json();
			})
			.then(function (data) {
				files.update((files) => {
					return {
						...files,
						[$exp.tabs[$exp.current_tab]]: {
							...files[$exp.tabs[$exp.current_tab]],
							errors: data['errors']
						}
					};
				});

				//  tabs[active_tab]["errors"] = data["errors"];
			}) // This will log the JSON response to the console
			.catch(function (error) {
				console.error('Error:', error);
			});
	}

	function newtab() {
		// Update the files store
		// Create a copy of the current tab's contents with updated content
		let updatedContents = {
			...$files[$exp.current_tab],
			content: value
		};

		// Update the contents in the files store
		files.update((store) => ({
			...store,
			[$exp.current_tab]: updatedContents
		}));

		value = '';

		files.update((currentFiles) => {
			const newFileId = Object.keys(currentFiles).length; // Calculate the new file ID
			//console.log(newFileId)
			const newFile = { title: checkFilenames(), content: 'Hello, World!', errors: [] };
			return { ...currentFiles, [newFileId]: newFile };
		});

		// Update the exp store
		exp.update((currentExp) => {
			const newTabId = Object.keys($files).length - 1; // Get the ID of the newly created tab
			const updatedTabs = [...currentExp.tabs, newTabId]; // Add the new tab ID
			return { ...currentExp, tabs: updatedTabs, current_tab: updatedTabs.length - 1 };
		});
	}

	function get(object, key, default_value) {
		var result = object[key];
		return typeof result !== 'undefined' ? result : default_value;
	}

	function loadSettings(settings_code = '') {
		fetch(`${api}/decode`, {
			method: 'POST',
			body: JSON.stringify({
				code: settings_code,
				linter: linter
			}),
			headers: {
				'Content-type': 'application/json',
				Accept: 'application/json'
			}
		})
			.then(function (res) {
				if (!res.ok) {
					throw new Error(res.statusText);
				}
				return res.json();
			})
			.then(function (data) {
				settings = data;
				console.log(settings)
				const categoryCounts = {};
				Object.entries(settings).forEach(([code, item]) => {
					const { category } = item;

					// Increment the count for the category
					if (!get(categoryCounts, category, false)) {
						categoryCounts[category] = [code];
					} else {
						categoryCounts[category].push(code);
					}
				});
				const temp = Object.keys(categoryCounts);
				temp.forEach((e) => {
					categorisedDisabled[e] = {
						items: [],
						max: categoryCounts[e].length,
						trues: categoryCounts[e]
					};
				});

				console.log(categorisedDisabled);

				ruleCount();
				createLink();
			}) // This will log the JSON response to the console
			.catch(function (error) {
				console.error('Error:', error);
			});
	}

	function createLink() {
		fetch(`${api}/encode`, {
			method: 'POST',
			body: JSON.stringify({
				disabled: disabled,
				linter: linter
			}),
			headers: {
				'Content-type': 'application/json',
				Accept: 'application/json'
			}
		})
			.then(function (res) {
				if (!res.ok) {
					throw new Error(res.statusText);
				}
				return res.json();
			})
			.then(function (data) {
				console.log(data['link']);
				link = window.location.origin + '?' + linter + '=' + data['link'];
			}) // This will log the JSON response to the console
			.catch(function (error) {
				console.error('Error:', error);
			});
	}
</script>

<svelte:head>
	<title
		>pep8plus - {$files[$exp.tabs[$exp.current_tab]].errors.length == 1 ? 'Error' : 'Errors'} ({$files[
			$exp.tabs[$exp.current_tab]
		].errors.length})</title
	>
</svelte:head>

<div class="container">
	<!-- Left Toolbar -->
	<div class="workspace workspace-sidedoc" style="width: {side_width + left_width}%">
		<div class="workspace-tabtools">
			<div class="panel-collapse" style="width: {side_width}vw;">
				<span
					class="material-symbols-outlined"
					on:click={() => {
						expand();
					}}
				>
					dock_to_right
				</span>
				<p class="bubble-right">{left_expand ? 'Expand' : 'Collapse'}</p>
			</div>
			<div class="panel-navtools">
				{#each nav_buttons as icon}
					<button class="material-symbols-outlined {icon == activeTab ? 'tab-active' : ''}">
						<span
							on:click={() => {
								activeTab = icon;
							}}
						>
							{icon}
						</span>
					</button>
				{/each}
			</div>
		</div>

		<div class="workspace-sidebar">
			<div
				class="workspace-sidetools"
				style="{main_width == 100 - left_width - side_width - right_width
					? ''
					: 'transition-delay: var(--transition-speed);'}; background-color: var({main_width ==
				100 - left_width - side_width - right_width
					? '--lm-fore-colour'
					: '--lm-back-colour'})"
			>
				<div class="panel-navtools" style="width: calc({side_width}vw - 1px);">
					<button on:click={rawCode}
						><span class="material-symbols-outlined"> raw_on </span>
						<p class="bubble-right">Raw Code</p>
					</button>
					<button
						on:click={() => (copyCode(), (url_copied = true))}
						on:mouseenter={() => (url_copied = false)}
					>
						<span class="material-symbols-outlined"> content_copy </span>
						<p class="bubble-right">{url_copied ? 'Copied!' : 'Copy Code'}</p>
					</button>
					<button on:click={downloadCode}
						><span class="material-symbols-outlined"> download </span>
						<p class="bubble-right">Download Code</p>
					</button>
					<button on:click={autofix}
						><span class="material-symbols-outlined"> reset_wrench </span>
						<p class="bubble-right">Partial Auto-fix</p>
					</button>
					<button
						><span class="material-symbols-outlined">
							<a
								href="https://github.com/amooo-ooo/pep8plus/issues/new/choose"
								target="_blank"
								rel="noopener noreferrer"
							>
								bug_report
							</a>
						</span>
						<p class="bubble-right">Report Bug</p>
					</button>
					<button
						><span>
							<a
								href="https://github.com/amooo-ooo/pep8plus"
								target="_blank"
								rel="noopener noreferrer"
							>
								<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" class="svelte-12zvzru"
									><title class="svelte-12zvzru">github</title><path
										fill="currentColor"
										d="M12,2A10,10,0,0,0,8.84,21.5c.5.08.66-.23.66-.5V19.31C6.73,19.91,6.14,18,6.14,18A2.69,2.69,0,0,0,5,16.5c-.91-.62.07-.6.07-.6a2.1,2.1,0,0,1,1.53,1,2.15,2.15,0,0,0,2.91.83,2.16,2.16,0,0,1,.63-1.34C8,16.17,5.62,15.31,5.62,11.5a3.87,3.87,0,0,1,1-2.71,3.58,3.58,0,0,1,.1-2.64s.84-.27,2.75,1a9.63,9.63,0,0,1,5,0c1.91-1.29,2.75-1,2.75-1a3.58,3.58,0,0,1,.1,2.64,3.87,3.87,0,0,1,1,2.71c0,3.82-2.34,4.66-4.57,4.91a2.39,2.39,0,0,1,.69,1.85V21c0,.27.16.59.67.5A10,10,0,0,0,12,2Z"
										class="svelte-12zvzru"
									></path></svg
								>
							</a>
						</span>
						<p class="bubble-right">GitHub Repo</p>
					</button>
				</div>
			</div>
			
			<div class="workspace-navmenu">
				{#if activeTab == 'folder'}
					<h3>File Explorer</h3>
					<div class="files">
						{#each Object.entries($files) as [key, file]}
							<div class="file">
								<p
									class={key == $exp.tabs[$exp.current_tab] ? 'active' : ''}
									on:click={() => updateTab(Number(key))}
								>
									{file.title}
								</p>
							</div>
						{/each}
					</div>
				{:else if activeTab == 'settings'}
					<h3>Summary</h3>
					<div class="summary">
						<p>Version: Python 3.10.11</p>
						<p>Rules Enabled: {rulecount}/{ruletotal}</p>
						<p>
							Linter: <select
								bind:value={linter}
								on:change={() => loadSettings('all')}
								id="lint-select"
							>
								{#each linters as item (item)}
									<option>{item}</option>
								{/each}
							</select>
						</p>
					</div>
					<h3>Share Ruleset</h3>
					<div class="share">
						<button
							on:click={() => (navigator.clipboard.writeText(link), (url_copied = true))}
							on:mouseenter={() => (url_copied = false)}
							><span class="material-symbols-outlined"> content_copy </span>
							<p class="bubble-top">{url_copied ? 'Copied!' : 'Copy Url'}</p>
						</button>
						<input bind:value={link} type="text" />
					</div>
					<h3>Settings</h3>
					<div
						class="settings"
						style="height: calc(100dvh - ((var(--tab-icon-gap) * 11) + (var(--tab-height))  + (.8rem * 5) + (.5rem * 2) + (1px	) + 2.7rem); overflow: auto;"
					>
						{#each Object.entries(settings) as [code, values], index}
							<!-- really disgusting code v feel free to fix it, it's 3 am ;-; -->
							{#if index}
								{@const previous = settings[Object.keys(settings)[index - 1]].category}
								{#if !(previous === values.category)}
									<div class="error seperator">
										<div class="header">
											{#if categorisedDisabled[values.category].items.length == 0}
												<span
													class="material-symbols-outlined"
													on:click={() => {
														superToggle('filled', values.category), createLink();
													}}
												>
													check_box
												</span>
											{:else if categorisedDisabled[values.category].items.length == categorisedDisabled[values.category].max}
												<span
													class="material-symbols-outlined"
													on:click={() => {
														superToggle('none', values.category), createLink();
													}}
												>
													check_box_outline_blank
												</span>
											{:else}
												<span
													class="material-symbols-outlined"
													on:click={() => {
														superToggle('ugh', values.category), createLink();
													}}
												>
													indeterminate_check_box
												</span>
											{/if}
											<h3>{values.category}</h3>
										</div>
									</div>
								{/if}
							{:else}
								<div class="error seperator-first">
									<div class="header">
										<span
											class="material-symbols-outlined"
											on:click={() => {
												toggleCheckbox(values.value, code), createLink();
											}}
										>
											{values.value ? 'check_box' : 'check_box_outline_blank'}
										</span>
										<h3>{values.category}</h3>
									</div>
								</div>
							{/if}
							<div class="error">
								<div class="header">
									<span
										class="material-symbols-outlined"
										on:click={() => {
											toggleCheckbox(values.value, code, values.category), createLink();
										}}
									>
										{values.value ? 'check_box' : 'check_box_outline_blank'}
									</span>
									<div class="error-code {Array.from(code)[0].toLowerCase()}">
										<div></div>
										<p>{code}</p>
									</div>
									<p>{values.name}</p>
								</div>
							</div>
						{/each}
					</div>
				{/if}
			</div>
		</div>
	</div>

	<!-- Workspace (e.g. tabs, code editor, etc) -->

	<div
		class="workspace workspace-main"
		style="width: calc({main_width}% - 2px); left: calc({main_displace}% + 1px)"
	>
		<div class="workspace-tabtools">
			{#each $exp.tabs as tab, index}
				<div
					class="{$exp.current_tab == index
						? 'workspace-tab-active'
						: 'workspace-tab-inactive'} tab"
					on:click={() => switchTabs(index)}
				>
					<div class="workspace-tab-inner">
						<p>{$files[tab]?.title}</p>

						<button
							on:click={() => removeTabAtIndex(index)}
							class="{$exp.current_tab == index
								? 'tab-close-active'
								: 'tab-close-inactive'} tab-close"
						>
							<span class="material-symbols-outlined"> close </span>
						</button>
					</div>
				</div>
			{/each}
			<div class="workspace-leftovers">
				<button on:click={newtab} class="tab-add">
					<span class="material-symbols-outlined"> add </span>
				</button>
			</div>
		</div>
		<div class="workspace-editor">
			<div class="workspace-headers">
				<div class="headers-left">
					{#each workspace_left_buttons as button}
						<button>
							<span class="material-symbols-outlined"> {button} </span>
						</button>
					{/each}
				</div>
				<div class="headers-centre">
					<span
						class="title"
						contenteditable
						bind:textContent={$files[$exp.tabs[$exp.current_tab]].title}
					></span>
				</div>
				<div class="headers-right">
					<button
						class={spin ? 'spin' : ''}
						id="refresh"
						on:click={() => {
							clearTimeout(timer), submit(), (spin = false);
						}}
					>
						<span class="material-symbols-outlined"> autorenew </span>
					</button>
				</div>
			</div>
			<CodeMirror
				bind:value
				lang={python()}
				theme={githubLight}
				styles={editor_settings}
				bind:this={editor}
			/>
			<!-- <p>{$files[$exp.tabs[$exp.current_tab]].content}</p> -->
		</div>
	</div>

	<div class="workspace workspace-sidedoc" style="width: {right_width}vw; margin-left: auto;">
		<div class="workspace-tabtools">
			<div class="panel-collapse" style="width: {side_width}vw; margin-left: auto;">
				<span
					class="material-symbols-outlined"
					on:click={() => {
						expand('right');
					}}
				>
					dock_to_left
				</span>
			</div>
		</div>

		<div class="workspace-sidebar">
			<div class="workspace-navmenu">
				<h3>
					{$files[$exp.tabs[$exp.current_tab]].errors.length == 1 ? 'Error' : 'Errors'} ({$files[
						$exp.tabs[$exp.current_tab]
					].errors.length})
				</h3>
				<div class="errors">
					{#each $files[$exp.tabs[$exp.current_tab]].errors as [line, column, code, description], index}
						<div
							class={selected_error == index ? 'error-active' : 'error'}
							on:click={() => {
								selected_error = index;
							}}
						>
							<div class="header">
								<div class="error-code {Array.from(code)[0].toLowerCase()}">
									<div></div>
									<p>{code}</p>
								</div>

								<p>
									{settings[code].name}
								</p>
								<p class="line">Ln {line}, Col {column}</p>
							</div>

							{#if selected_error == index}
								<div class="contents">
									<!-- lmao tf is this -->
									<p>
										{#if description}{#if description[0].match(/[a-zA-Z]/)}{description[0].toUpperCase()}{description.slice(
													1
												)}{:else}{description}{/if}{#if description[description.length - 1] !== '.'}.{/if}{:else}No
											description available.{/if}
									</p>
									<p class="category">
										source: {settings[code].category}
									</p>
								</div>
							{/if}
						</div>
					{/each}
				</div>
			</div>
		</div>
	</div>
</div>
<footer>
	<div id="footer_count">
		<p>{fileSizeDisplay} KB</p>
		<p>Lines: {lineCount}</p>
	</div>
	<div id="footer_details">
		<p>Spaces: 4</p>
		<p>UTF-8</p>
		<p>Python {pyVersion}</p>
	</div>
</footer>

<!-- <div class="workspace workspace-sidedoc"></div> -->
