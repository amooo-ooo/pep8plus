<script lang="js">
	import CodeMirror from "svelte-codemirror-editor";
	import { python } from "@codemirror/lang-python";
	import { githubDark, githubLight } from "@uiw/codemirror-theme-github";

	let linters = ["Ruff", "Flake8", "Pylint"];
	let rulecount = 0;
	let value = ``;
	let errors = [];
	let visible = false;
	let themes = {
		dark: {
			editor: githubDark,
			colours: {
				primary: "#0d1117",
				secondary: "#161b22",
				buttons: "#1f242c",
				buttons_hover: "#21262c",
				outline: "#30363d",
				text: "#e1e9ee",
				line_select: "#21212c",
				highlight: "#1c1a15",
				text_description: "#7d8590",
			},
		},

		light: {
			editor: githubLight,
			colours: {
				primary: "#ffffff",
				secondary: "#f6f8fa",
				buttons: "#eaeef2",
				buttons_hover: "#f0f2f4",
				outline: "#d0d7de",
				text: "#1f2328",
				line_select: "#f1fbff",
				highlight: "#fffadc",
				text_description: "#656d76",
			},
		},
	};
	let theme = "dark";

	let root = window.document.querySelector(":root");
	function updateCSS() {
		root.style.setProperty("--active-main", themes[theme].colours.primary);
		root.style.setProperty(
			"--active-second",
			themes[theme].colours.secondary
		);
		root.style.setProperty(
			"--active-buttons",
			themes[theme].colours.buttons
		);
		root.style.setProperty(
			"--active-buttons-hover",
			themes[theme].colours.buttons_hover
		);
		root.style.setProperty(
			"--active-outline",
			themes[theme].colours.outline
		);
		root.style.setProperty("--active-text", themes[theme].colours.text);
		root.style.setProperty(
			"--active-line-select",
			themes[theme].colours.line_select
		);
		root.style.setProperty(
			"--active-highlight",
			themes[theme].colours.highlight
		);
		root.style.setProperty(
			"--active-text-description",
			themes[theme].colours.text_description
		);
	}

	function submit() {
		let disabled = [];
		for (let i in settings) {
			for (let e in settings[i]) {
				let value = settings[i][e]["value"];
				if (!value) {
					disabled.push(e);
				}
			}
		}

		fetch("./check", {
			method: "POST",
			body: JSON.stringify({
				code: value,
				disable: disabled,
				linter: linter,
			}),
			headers: {
				"Content-type": "application/json",
				Accept: "application/json",
			},
		})
			.then(function (res) {
				if (!res.ok) {
					throw new Error(res.statusText);
				}
				return res.json();
			})
			.then(function (data) {
				errors = data["errors"];
			}) // This will log the JSON response to the console
			.catch(function (error) {
				console.error("Error:", error);
			});
	}

	function loadSettings(settings_code) {
		fetch("./decode", {
			method: "POST",
			body: JSON.stringify({
				settings: settings_code,
				linter: linter,
			}),
			headers: {
				"Content-type": "application/json",
				Accept: "application/json",
			},
		})
			.then(function (res) {
				if (!res.ok) {
					throw new Error(res.statusText);
				}
				return res.json();
			})
			.then(function (data) {
				settings = data;
				ruleCount();
			}) // This will log the JSON response to the console
			.catch(function (error) {
				console.error("Error:", error);
			});
	}

	function createLink() {
		let disabled = [];
		for (let i in settings) {
			for (let e in settings[i]) {
				let value = settings[i][e]["value"];
				if (!value) {
					disabled.push(e);
				}
			}
		}

		console.log(settings);

		fetch("./encode", {
			method: "POST",
			body: JSON.stringify({
				disabled: disabled,
				linter: linter,
			}),
			headers: {
				"Content-type": "application/json",
				Accept: "application/json",
			},
		})
			.then(function (res) {
				if (!res.ok) {
					throw new Error(res.statusText);
				}
				return res.json();
			})
			.then(function (data) {
				alert(
					window.location.origin + "?" + linter + "=" + data["link"]
				);
			}) // This will log the JSON response to the console
			.catch(function (error) {
				console.error("Error:", error);
			});
	}

	function settingsShow() {
		visible = !visible;
	}

	function toggleGroup(category) {
		for (let i in settings[category]) {
			settings[category][i]["value"] = !settings[category][i]["value"];
		}
	}

	let url = new URL(window.location.toLocaleString()).searchParams;

	let settings = {};
	let disabled = {};
	let linter = "all";

	if (url.has("Ruff")) {
		linter = "Ruff";
	} else if (url.has("Flake8")) {
		linter = "Flake8";
	} else if (url.has("Pylint")) {
		linter = "Pylint";
	}

	if (linter == "all") {
		linter = "Flake8";
		loadSettings("all");
	} else {
		loadSettings(url.get(linter));
	}

	let record;
	function highlight(lineNumber) {
		var lines = document.getElementsByClassName("cm-line");
		var check = document.getElementsByClassName("cm-gutterElement");

		for (var i = 1; i <= lines.length; i++) {
			if (record) {
				record.classList.remove("highlight");
			}
			if (check[i].textContent == lineNumber.toString()) {
				lines[i - 1].classList.add("highlight");
				lines[i - 1].scrollIntoView({
					behavior: "smooth",
					block: "center",
				});
				record = lines[i - 1];
				break;
			} else if (Number(check[i].textContent) >= lineNumber) {
				lines[i - 2].classList.add("highlight");
				lines[i - 2].scrollIntoView({
					behavior: "smooth",
					block: "center",
				});
				record = lines[i - 2];
				break;
			}
		}
	}

	let fileSizeDisplay = "0";
	let lineCount = "0";
	function fileSize() {
		var sizeInBytes = new Blob([value]).size;
		fileSizeDisplay = (sizeInBytes / 1024).toFixed(2).toString();
		lineCount = value.split("\n").length.toString();
	}

	function copyCode() {
		navigator.clipboard.writeText(value);
	}

	function ruleCount() {
		rulecount = 0;
		for (let i in settings) {
			for (let e in settings[i]) {
				let value = settings[i][e]["value"];
				if (value) {
					rulecount++;
				}
			}
		}
	}

	function rawCode() {
		var blob = new Blob([value], { type: "text/plain" });
		var url = URL.createObjectURL(blob);
		window.open(url);
	}

	function downloadCode() {
		var blob = new Blob([value], { type: "text/plain" });

		var a = document.createElement("a");
		a.href = URL.createObjectURL(blob);
		a.download = "pep8plus_untitled.py";

		document.body.appendChild(a);
		a.click();
		document.body.removeChild(a);
	}

	updateCSS()
</script>

<main>
	<div id="editor-panel">
		<div id="editor-header" style="border-color">
			<div id="lint-mode">
				<button
					on:click={() => ((theme = "dark"), updateCSS())}
					class={theme === "dark" ? "selected" : "unselected"}
					>Dark</button
				>
				<button
					on:click={() => ((theme = "light"), updateCSS())}
					class={theme === "light" ? "selected" : "unselected"}
					>Light</button
				>
			</div>
			<h4 id="file-info">{lineCount} lines · {fileSizeDisplay} KB</h4>

			<div class="button-stack">
				<button on:click={rawCode}><p>Raw</p></button>
				<button on:click={copyCode}
					><svg class="icon" fill="currentColor"
						><path
							d="M0 6.75C0 5.784.784 5 1.75 5h1.5a.75.75 0 0 1 0 1.5h-1.5a.25.25 0 0 0-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 0 0 .25-.25v-1.5a.75.75 0 0 1 1.5 0v1.5A1.75 1.75 0 0 1 9.25 16h-7.5A1.75 1.75 0 0 1 0 14.25Z"
						/><path
							d="M5 1.75C5 .784 5.784 0 6.75 0h7.5C15.216 0 16 .784 16 1.75v7.5A1.75 1.75 0 0 1 14.25 11h-7.5A1.75 1.75 0 0 1 5 9.25Zm1.75-.25a.25.25 0 0 0-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 0 0 .25-.25v-7.5a.25.25 0 0 0-.25-.25Z"
						/></svg
					></button
				>
				<button on:click={downloadCode}
					><svg class="icon" fill="currentColor"
						><path
							d="M2.75 14A1.75 1.75 0 0 1 1 12.25v-2.5a.75.75 0 0 1 1.5 0v2.5c0 .138.112.25.25.25h10.5a.25.25 0 0 0 .25-.25v-2.5a.75.75 0 0 1 1.5 0v2.5A1.75 1.75 0 0 1 13.25 14Z"
						/><path
							d="M7.25 7.689V2a.75.75 0 0 1 1.5 0v5.689l1.97-1.969a.749.749 0 1 1 1.06 1.06l-3.25 3.25a.749.749 0 0 1-1.06 0L4.22 6.78a.749.749 0 1 1 1.06-1.06l1.97 1.969Z"
						/></svg
					></button
				>
			</div>
		</div>
		<div id="editor">
			<CodeMirror
				bind:value
				lang={python()}
				tabSize="4"
				on:change={fileSize}
				theme={themes[theme].editor}
				styles={{
					"&": {
						height: "32rem",
						border: "1px solid var(--active-outline)",
						borderRadius: "0 0 0.5rem 0.5rem",
						overflow: "auto",
					},
					".cm-gutters": {
						backgroundColor: "var(--active-main)",
						borderRight: "transparent",
					},
					".cm-lineNumbers": { minWidth: "3.6vw" },
					".cm-foldGutter": { width: "1	vw" },
					".cm-wrap": { height: "100%" },
					".cm-scroller": { overflow: "auto" },
					".cm-activeLine": {
						backgroundColor: "var(--active-line-select)",
					},
					".cm-activeLineGutter": {
						backgroundColor: "var(--active-line-select)",
					},
				}}
			/>
		</div>
		<button id="submit-button" on:click={submit}>Submit</button>
	</div>

	<div id="settings-panel">
		<div id="settings-header">
			<div class="text-stack">
				<h3>Problems {errors.length}</h3>
				<h3>Rules {rulecount}</h3>
			</div>

			<select
				bind:value={linter}
				on:change={() => loadSettings("all")}
				id="lint-select"
			>
				{#each linters as item (item)}
					<option>{item}</option>
				{/each}
			</select>

			<div id="settings-button">
				<button on:click={settingsShow}
					><svg class="icon" fill="currentColor"
						><path
							d="M8 0a8.2 8.2 0 0 1 .701.031C9.444.095 9.99.645 10.16 1.29l.288 1.107c.018.066.079.158.212.224.231.114.454.243.668.386.123.082.233.09.299.071l1.103-.303c.644-.176 1.392.021 1.82.63.27.385.506.792.704 1.218.315.675.111 1.422-.364 1.891l-.814.806c-.049.048-.098.147-.088.294.016.257.016.515 0 .772-.01.147.038.246.088.294l.814.806c.475.469.679 1.216.364 1.891a7.977 7.977 0 0 1-.704 1.217c-.428.61-1.176.807-1.82.63l-1.102-.302c-.067-.019-.177-.011-.3.071a5.909 5.909 0 0 1-.668.386c-.133.066-.194.158-.211.224l-.29 1.106c-.168.646-.715 1.196-1.458 1.26a8.006 8.006 0 0 1-1.402 0c-.743-.064-1.289-.614-1.458-1.26l-.289-1.106c-.018-.066-.079-.158-.212-.224a5.738 5.738 0 0 1-.668-.386c-.123-.082-.233-.09-.299-.071l-1.103.303c-.644.176-1.392-.021-1.82-.63a8.12 8.12 0 0 1-.704-1.218c-.315-.675-.111-1.422.363-1.891l.815-.806c.05-.048.098-.147.088-.294a6.214 6.214 0 0 1 0-.772c.01-.147-.038-.246-.088-.294l-.815-.806C.635 6.045.431 5.298.746 4.623a7.92 7.92 0 0 1 .704-1.217c.428-.61 1.176-.807 1.82-.63l1.102.302c.067.019.177.011.3-.071.214-.143.437-.272.668-.386.133-.066.194-.158.211-.224l.29-1.106C6.009.645 6.556.095 7.299.03 7.53.01 7.764 0 8 0Zm-.571 1.525c-.036.003-.108.036-.137.146l-.289 1.105c-.147.561-.549.967-.998 1.189-.173.086-.34.183-.5.29-.417.278-.97.423-1.529.27l-1.103-.303c-.109-.03-.175.016-.195.045-.22.312-.412.644-.573.99-.014.031-.021.11.059.19l.815.806c.411.406.562.957.53 1.456a4.709 4.709 0 0 0 0 .582c.032.499-.119 1.05-.53 1.456l-.815.806c-.081.08-.073.159-.059.19.162.346.353.677.573.989.02.03.085.076.195.046l1.102-.303c.56-.153 1.113-.008 1.53.27.161.107.328.204.501.29.447.222.85.629.997 1.189l.289 1.105c.029.109.101.143.137.146a6.6 6.6 0 0 0 1.142 0c.036-.003.108-.036.137-.146l.289-1.105c.147-.561.549-.967.998-1.189.173-.086.34-.183.5-.29.417-.278.97-.423 1.529-.27l1.103.303c.109.029.175-.016.195-.045.22-.313.411-.644.573-.99.014-.031.021-.11-.059-.19l-.815-.806c-.411-.406-.562-.957-.53-1.456a4.709 4.709 0 0 0 0-.582c-.032-.499.119-1.05.53-1.456l.815-.806c.081-.08.073-.159.059-.19a6.464 6.464 0 0 0-.573-.989c-.02-.03-.085-.076-.195-.046l-1.102.303c-.56.153-1.113.008-1.53-.27a4.44 4.44 0 0 0-.501-.29c-.447-.222-.85-.629-.997-1.189l-.289-1.105c-.029-.11-.101-.143-.137-.146a6.6 6.6 0 0 0-1.142 0ZM11 8a3 3 0 1 1-6 0 3 3 0 0 1 6 0ZM9.5 8a1.5 1.5 0 1 0-3.001.001A1.5 1.5 0 0 0 9.5 8Z"
						/></svg
					></button
				>
			</div>
		</div>

		{#if visible}
			<div id="settings-display">
				<form>
					{#each Object.keys(settings) as category}
						<div class="category-title">
							{category}
							<input
								class="category-toggle"
								type="button"
								on:click={() => (toggleGroup(category), ruleCount())}
								value="Toggle"
							/>
						</div>
						<div class="group">
							{#each Object.entries(settings[category]) as [code, info]}
								<div class="error-row">
									<input
										type="checkbox"
										name={code}
										bind:checked={info.value}
										on:change={ruleCount}
									/>

									<div
										class="{code[0].toLowerCase()} error-code"
									>
										<div />
										<p>{code}</p>
									</div>
									<div class="error-text">
										{info.name}
									</div>
								</div>
							{/each}
						</div>{/each}
				</form>
				<input
					id="create-link"
					type="button"
					value="Create Link"
					on:click={createLink}
				/>
			</div>
		{/if}

		{#if !visible}
			<div id="error-display">
				{#each errors as error}
					<div class="error-row" on:click={() => highlight(error[0])}>
						<div class="{error[2][0].toLowerCase()} error-code">
							<div />
							<p>{error[2]}</p>
						</div>
						<div class="error-text">
							<span class="error-location"
								>{error[0]}, {error[1]}</span
							>
							{error[3]}
						</div>
					</div>
				{/each}
			</div>
		{/if}
	</div>
</main>
