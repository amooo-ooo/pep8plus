<script>
    import CodeMirror from "svelte-codemirror-editor";
    import { python } from "@codemirror/lang-python";
    import { githubDark, githubLight } from "@uiw/codemirror-theme-github";
    import 'codemirror/lib/codemirror.css';

    let linters = ["Ruff", "Flake8", "Pylint"];
    let errors = [];
    let tabs = [{ name: "untitled.py", contents: "", errors: [] }];
    let active_tab = 0;
    let value;
    let theme = "dark";
    let pyVersion = `3.10.11`;
    let show_info = false;
    let rulecount;
    let ruletotal;
    let ruleshow = {};
    let workspace = true;
    let rules = true;
    let share = true;
    let link = "http://pep8plus.com/";
    let categories = {};

    let themes = {
        dark: {
            editor: githubDark,
            colours: {
                primary: "#151515",
                secondary: "#25272b",
                buttons: "#1f242c",
                buttons_hover: "#21262c",
                outline: "#30363d",
                text: "#e1e9ee",
                line_select: "#21212c",
                highlight: "#3d362f",
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
                tabs[active_tab]["errors"] = data["errors"];
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
                for (let i in settings) {
                    ruleshow[i] = false;
                }
                for (let i in settings) {
                    for (let e of Object.keys(settings[i])) {
                        categories[e] = i;
                    }
                }
                ruleCount();
                createLink();
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
                link =
                    window.location.origin + "?" + linter + "=" + data["link"];
            }) // This will log the JSON response to the console
            .catch(function (error) {
                console.error("Error:", error);
            });
    }

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

    function newTab() {
        tabs = [...tabs, { name: "untitled.py", contents: "", errors: [] }];
        switchTab(tabs.length - 1);
    }

    function switchTab(index) {
        tabs[active_tab]["contents"] = value;
        active_tab = index;
        value = tabs[active_tab]["contents"];
        fileSize();
    }

    function deleteTab(index) {
        if (tabs.length != 1) {
            tabs.splice(index, 1);
            tabs = tabs;
            if (index == 0) {
                active_tab = 0;
                value = tabs[active_tab]["contents"];
            } else if (index == active_tab) {
                active_tab = index - 1;
                value = tabs[active_tab]["contents"];
            } else if (index < active_tab) {
                active_tab = index;
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

    function ruleCount() {
        rulecount = 0;
        ruletotal = 0;
        for (let i in settings) {
            for (let e in settings[i]) {
                let value = settings[i][e]["value"];
                if (value) {
                    rulecount++;
                }
                ruletotal++;
            }
        }
    }

    function toggleGroup(category) {
        for (let i in settings[category]) {
            settings[category][i]["value"] = !settings[category][i]["value"];
        }
    }

    function copyCode() {
        navigator.clipboard.writeText(value);
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
        a.download = tabs[active_tab]["name"];

        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }

    updateCSS();
</script>

<main>
    <div id="header">
        <div id="logo">
            <img src="favicon.png" alt="pep8plus logo" />
        </div>
        <div id="title">
            <div id="git_path">
                <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path
                        fill="currentColor"
                        d="M12,2A10,10,0,0,0,8.84,21.5c.5.08.66-.23.66-.5V19.31C6.73,19.91,6.14,18,6.14,18A2.69,2.69,0,0,0,5,16.5c-.91-.62.07-.6.07-.6a2.1,2.1,0,0,1,1.53,1,2.15,2.15,0,0,0,2.91.83,2.16,2.16,0,0,1,.63-1.34C8,16.17,5.62,15.31,5.62,11.5a3.87,3.87,0,0,1,1-2.71,3.58,3.58,0,0,1,.1-2.64s.84-.27,2.75,1a9.63,9.63,0,0,1,5,0c1.91-1.29,2.75-1,2.75-1a3.58,3.58,0,0,1,.1,2.64,3.87,3.87,0,0,1,1,2.71c0,3.82-2.34,4.66-4.57,4.91a2.39,2.39,0,0,1,.69,1.85V21c0,.27.16.59.67.5A10,10,0,0,0,12,2Z"
                    />
                </svg>
                <p>amooo-ooo / pep8plus / master</p>
            </div>
        </div>
    </div>
    <div id="body">
        <div id="menubar">
            <div id="app">
                
                <button name="settings" on:click={() => (show_info = !show_info)}
                    ><svg
                        viewBox="0 0 192 192"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        ><path
                            fill="currentColor"
                            d="m80.16 29.054-5.958-.709 5.958.71Zm31.68 0-5.958.71 5.958-.71Zm34.217 19.756-2.365-5.515 2.365 5.514Zm10.081 3.352 5.196-3-5.196 3Zm7.896 13.676 5.196-3-5.196 3Zm-2.137 10.407-3.594-4.805 3.594 4.805Zm0 39.51 3.593-4.805-3.593 4.805Zm2.137 10.407 5.196 3-5.196-3Zm-7.896 13.676-5.196-3 5.196 3Zm-10.081 3.353 2.364-5.515-2.364 5.515Zm-34.217 19.755 5.958.709-5.958-.709Zm-31.68 0-5.958.709 5.958-.709Zm-34.217-19.755-2.364-5.515 2.364 5.515Zm-10.08-3.353-5.197 3 5.196-3Zm-7.897-13.676 5.196-3-5.196 3Zm2.137-10.407 3.594 4.805-3.594-4.805Zm0-39.51L26.51 81.05l3.593-4.805Zm-2.137-10.407 5.196 3-5.196-3Zm7.896-13.676-5.196-3 5.196 3Zm10.081-3.352-2.364 5.514 2.364-5.514Zm7.85 3.365-2.365 5.515 2.364-5.515Zm0 87.65 2.364 5.514-2.365-5.514ZM36.235 111.17l-3.594-4.805 3.594 4.805Zm76.823 41.535 5.958.71-5.958-.71Zm39.854-69.742-3.593-4.805 3.593 4.805Zm-16.369-30.074 2.364 5.514-2.364-5.514Zm-23.485-13.594-5.958.709 5.958-.71ZM88.104 16a14 14 0 0 0-13.902 12.345l11.916 1.419A2 2 0 0 1 88.104 28V16Zm15.792 0H88.104v12h15.792V16Zm13.902 12.345A14 14 0 0 0 103.896 16v12a2 2 0 0 1 1.986 1.764l11.916-1.419Zm1.219 10.24-1.219-10.24-11.916 1.419 1.219 10.24 11.916-1.419Zm24.675 4.71-9.513 4.08 4.729 11.028 9.513-4.08-4.729-11.028Zm17.642 5.867a14 14 0 0 0-17.642-5.867l4.729 11.029a2 2 0 0 1 2.521.838l10.392-6Zm7.896 13.676-7.896-13.676-10.392 6 7.896 13.676 10.392-6Zm-3.74 18.212a14 14 0 0 0 3.74-18.212l-10.392 6a2 2 0 0 1-.535 2.602l7.187 9.61Zm-8.984 6.718 8.984-6.718-7.187-9.61-8.983 6.718 7.186 9.61Zm8.984 23.182-8.984-6.718-7.186 9.61 8.983 6.718 7.187-9.61Zm3.74 18.212a14 14 0 0 0-3.74-18.212l-7.187 9.61a2 2 0 0 1 .535 2.602l10.392 6Zm-7.896 13.676 7.896-13.676-10.392-6-7.896 13.676 10.392 6Zm-17.642 5.867a14 14 0 0 0 17.642-5.867l-10.392-6a2.001 2.001 0 0 1-2.521.838l-4.729 11.029Zm-9.513-4.08 9.513 4.08 4.729-11.029-9.512-4.079-4.73 11.028Zm-16.381 19.03 1.219-10.24-11.916-1.419-1.219 10.24 11.916 1.419ZM103.896 176a14 14 0 0 0 13.902-12.345l-11.916-1.419a2 2 0 0 1-1.986 1.764v12Zm-15.792 0h15.792v-12H88.104v12Zm-13.902-12.345A14 14 0 0 0 88.104 176v-12a2 2 0 0 1-1.986-1.764l-11.916 1.419Zm-1.012-8.504 1.012 8.504 11.916-1.419-1.012-8.504-11.916 1.419ZM51.428 134.31l-7.85 3.366 4.73 11.029 7.849-3.366-4.73-11.029Zm-7.85 3.366a2 2 0 0 1-2.52-.838l-10.392 6a14 14 0 0 0 17.642 5.867l-4.73-11.029Zm-2.52-.838-7.896-13.676-10.392 6 7.896 13.676 10.392-6Zm-7.896-13.676a2 2 0 0 1 .535-2.602l-7.187-9.61a14 14 0 0 0-3.74 18.212l10.392-6Zm.535-2.602 6.132-4.585-7.187-9.61-6.132 4.585 7.187 9.61ZM26.51 81.05l6.132 4.586 7.187-9.61-6.132-4.586-7.187 9.61Zm-3.74-18.212a14 14 0 0 0 3.74 18.212l7.187-9.61a2 2 0 0 1-.535-2.602l-10.392-6Zm7.896-13.676L22.77 62.838l10.392 6 7.896-13.676-10.392-6Zm17.642-5.867a14 14 0 0 0-17.642 5.867l10.392 6a2 2 0 0 1 2.52-.838l4.73-11.029Zm7.849 3.366-7.85-3.366-4.729 11.029 7.85 3.366 4.729-11.029Zm18.045-18.316-1.012 8.504 11.916 1.419 1.012-8.504-11.916-1.419Zm-1.754 27.552c6.078-3.426 11.69-9.502 12.658-17.63L73.19 36.85c-.382 3.209-2.769 6.415-6.635 8.595l5.893 10.453Zm-21.02 1.793c7.284 3.124 15.055 1.57 21.02-1.793l-5.893-10.453c-3.704 2.088-7.481 2.468-10.398 1.217l-4.73 11.029ZM49 96c0-7.1-2.548-15.022-9.171-19.975l-7.187 9.61C35.36 87.668 37 91.438 37 96h12Zm23.448 40.103c-5.965-3.363-13.736-4.917-21.02-1.793l4.729 11.029c2.917-1.251 6.694-.871 10.398 1.218l5.893-10.454Zm-32.62-20.128C46.452 111.022 49 103.1 49 96H37c0 4.563-1.64 8.333-4.358 10.365l7.187 9.61Zm78.679 19.575c-5.536 3.298-10.517 8.982-11.406 16.446l11.916 1.419c.329-2.765 2.318-5.582 5.632-7.557l-6.142-10.308Zm20.402-1.953c-7.094-3.042-14.669-1.463-20.402 1.953l6.142 10.308c3.382-2.015 6.872-2.372 9.53-1.233l4.73-11.028Zm-53.803 20.135c-.968-8.127-6.58-14.202-12.658-17.629l-5.893 10.454c3.866 2.179 6.253 5.385 6.635 8.594l11.916-1.419ZM141 96c0 6.389 2.398 13.414 8.32 17.842l7.186-9.61C154.374 102.638 153 99.668 153 96h-12Zm8.32-17.842C143.398 82.586 141 89.61 141 96h12c0-3.668 1.374-6.638 3.506-8.232l-7.186-9.61ZM118.507 56.45c5.733 3.416 13.308 4.995 20.401 1.953l-4.729-11.029c-2.658 1.14-6.148.782-9.53-1.233l-6.142 10.31Zm-11.406-16.446c.889 7.464 5.87 13.148 11.406 16.446l6.142-10.309c-3.314-1.974-5.303-4.79-5.632-7.556l-11.916 1.419Z"
                        /><path
                            stroke="currentColor"
                            stroke-linecap="round"
                            stroke-linejoin="round"
                            stroke-width="12"
                            d="M96 120c13.255 0 24-10.745 24-24s-10.745-24-24-24-24 10.745-24 24 10.745 24 24 24Z"
                        /></svg
                    ></button
                >
                <button
                    name="github"
                    onclick=" window.open('https://github.com/amooo-ooo/pep8plus','_blank')"
                    ><svg
                        viewBox="0 0 24 24"
                        xmlns="http://www.w3.org/2000/svg"
                    >
                        <title>github</title>
                        <path
                            fill="currentColor"
                            d="M12,2A10,10,0,0,0,8.84,21.5c.5.08.66-.23.66-.5V19.31C6.73,19.91,6.14,18,6.14,18A2.69,2.69,0,0,0,5,16.5c-.91-.62.07-.6.07-.6a2.1,2.1,0,0,1,1.53,1,2.15,2.15,0,0,0,2.91.83,2.16,2.16,0,0,1,.63-1.34C8,16.17,5.62,15.31,5.62,11.5a3.87,3.87,0,0,1,1-2.71,3.58,3.58,0,0,1,.1-2.64s.84-.27,2.75,1a9.63,9.63,0,0,1,5,0c1.91-1.29,2.75-1,2.75-1a3.58,3.58,0,0,1,.1,2.64,3.87,3.87,0,0,1,1,2.71c0,3.82-2.34,4.66-4.57,4.91a2.39,2.39,0,0,1,.69,1.85V21c0,.27.16.59.67.5A10,10,0,0,0,12,2Z"
                        />
                    </svg></button
                >
            </div>
        </div>
        {#if show_info}
            <div id="info_panel">
                <div class="workspace-section">
                    <button
                        on:click={() => (workspace = !workspace)}
                        class="reveal {workspace ? 'rev-down' : 'rev-right'}"
                    >
                        <svg
                            fill="currentColor"
                            version="1.1"
                            id="Layer_1"
                            xmlns="http://www.w3.org/2000/svg"
                            xmlns:xlink="http://www.w3.org/1999/xlink"
                            viewBox="0 0 24 24"
                            xml:space="preserve"
                        >
                            <style type="text/css">
                                .st0 {
                                    fill: none;
                                }
                            </style>
                            <path d="M9,18l7-6L9,6V18z" />
                            <rect class="st0" width="24" height="24" />
                            <rect class="st0" width="24" height="24" />
                        </svg>
                    </button>
                    <h4>Workspace Info</h4>
                </div>
                {#if workspace}
                    <div id="workspace-info">
                        <ul>
                            <div><p>Python: {pyVersion}</p></div>
                            <div>
                                <p>Linter:</p>
                                <select
                                    bind:value={linter}
                                    on:change={() => loadSettings("all")}
                                    id="lint-select"
                                >
                                    {#each linters as item (item)}
                                        <option>{item}</option>
                                    {/each}
                                </select>
                            </div>
                            <div><p>Rules: {rulecount}/{ruletotal}</p></div>
                        </ul>
                    </div>
                {/if}
                <div class="workspace-section">
                    <button
                        on:click={() => (share = !share)}
                        class="reveal {share ? 'rev-down' : 'rev-right'}"
                    >
                        <svg
                            fill="currentColor"
                            version="1.1"
                            id="Layer_1"
                            xmlns="http://www.w3.org/2000/svg"
                            xmlns:xlink="http://www.w3.org/1999/xlink"
                            viewBox="0 0 24 24"
                            xml:space="preserve"
                        >
                            <style type="text/css">
                                .st0 {
                                    fill: none;
                                }
                            </style>
                            <path d="M9,18l7-6L9,6V18z" />
                            <rect class="st0" width="24" height="24" />
                            <rect class="st0" width="24" height="24" />
                        </svg>
                    </button>
                    <h4>Share Workspace Settings</h4>
                </div>
                {#if share}
                    <div id="workspace-share">
                        <div><p>Share URL</p></div>
                        <div>
                            <input
                                name="link"
                                type="text"
                                bind:value={link}
                                placeholder="http://pep8plus.com/"
                            />
                        </div>
                        <div>
                            <button
                                on:click={() =>
                                    navigator.clipboard.writeText(link)}
                                >Copy link</button
                            >
                        </div>
                    </div>
                {/if}
                <div class="workspace-section">
                    <button
                        on:click={() => (rules = !rules)}
                        class="reveal {rules ? 'rev-down' : 'rev-right'}"
                    >
                        <svg
                            fill="currentColor"
                            version="1.1"
                            id="Layer_1"
                            xmlns="http://www.w3.org/2000/svg"
                            xmlns:xlink="http://www.w3.org/1999/xlink"
                            viewBox="0 0 24 24"
                            xml:space="preserve"
                        >
                            <style type="text/css">
                                .st0 {
                                    fill: none;
                                }
                            </style>
                            <path d="M9,18l7-6L9,6V18z" />
                            <rect class="st0" width="24" height="24" />
                            <rect class="st0" width="24" height="24" />
                        </svg>
                    </button>
                    <h4>Rules</h4>
                </div>
                {#if rules}<div id="workspace-rules">
                        {#each Object.keys(settings) as category}
                            <div class="category-title">
                                <button
                                    on:click={() =>
                                        (ruleshow[category] =
                                            !ruleshow[category])}
                                    class="reveal {ruleshow[category]
                                        ? 'rev-down'
                                        : 'rev-right'}"
                                >
                                    <svg
                                        fill="currentColor"
                                        version="1.1"
                                        id="Layer_1"
                                        xmlns="http://www.w3.org/2000/svg"
                                        xmlns:xlink="http://www.w3.org/1999/xlink"
                                        viewBox="0 0 24 24"
                                        xml:space="preserve"
                                    >
                                        <style type="text/css">
                                            .st0 {
                                                fill: none;
                                            }
                                        </style>
                                        <path d="M9,18l7-6L9,6V18z" />
                                        <rect
                                            class="st0"
                                            width="24"
                                            height="24"
                                        />
                                        <rect
                                            class="st0"
                                            width="24"
                                            height="24"
                                        />
                                    </svg>
                                </button>
                                <p>{category}</p>
                                <input
                                    class="category-toggle"
                                    type="button"
                                    on:click={() => (
                                        toggleGroup(category),
                                        ruleCount(),
                                        createLink()
                                    )}
                                    value="Toggle"
                                />
                                <!--<p class="category-count">{Object.keys(settings[category]).length}</p>-->
                            </div>
                            {#if ruleshow[category]}
                                {#each Object.entries(settings[category]) as [code, info]}
                                    <div class="error-row-display">
                                        <input
                                            type="checkbox"
                                            name={code}
                                            bind:checked={info.value}
                                            on:change={() => (
                                                ruleCount(), createLink()
                                            )}
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
                            {/if}
                        {/each}
                    </div>
                {/if}
            </div>
        {/if}

        <div id="main">
            <div id="editor" class={show_info ? "v33" : ""}>
                <header>
                    <div id="tab_menu">
                        {#each tabs as tab, index}
                            <div
                                class="tab {index === active_tab
                                    ? 'active-tab'
                                    : ''}"
                            >
                                <button on:click={() => switchTab(index)}>
                                    <img
                                        src="/icons/python.svg"
                                        alt="python logo."
                                    />
                                    <p>{tab["name"]}</p>
                                </button>
                                <button
                                    class="close"
                                    on:click={() => deleteTab(index)}
                                >
                                    <svg
                                        viewBox="0 0 24 24"
                                        fill="none"
                                        xmlns="http://www.w3.org/2000/svg"
                                        ><g
                                            id="SVGRepo_bgCarrier"
                                            stroke-width="0"
                                        /><g
                                            id="SVGRepo_tracerCarrier"
                                            stroke-linecap="round"
                                            stroke-linejoin="round"
                                        /><g id="SVGRepo_iconCarrier">
                                            <path
                                                d="M16 8L8 16M8.00001 8L16 16"
                                                stroke="currentColor"
                                                stroke-width="2"
                                                stroke-linecap="round"
                                                stroke-linejoin="round"
                                            />
                                        </g></svg
                                    >
                                </button>
                            </div>
                        {/each}
                    </div>
                    <button id="add_tab" on:click={newTab}
                        ><svg
                            viewBox="0 -0.5 21 21"
                            version="1.1"
                            xmlns="http://www.w3.org/2000/svg"
                            xmlns:xlink="http://www.w3.org/1999/xlink"
                            fill="fillColour"
                            ><g id="SVGRepo_bgCarrier" stroke-width="0" /><g
                                id="SVGRepo_tracerCarrier"
                                stroke-linecap="round"
                                stroke-linejoin="round"
                            /><g id="SVGRepo_iconCarrier">
                                <g
                                    id="Page-1"
                                    stroke="none"
                                    stroke-width="1"
                                    fill="none"
                                    fill-rule="evenodd"
                                >
                                    <g
                                        id="Dribbble-Light-Preview"
                                        transform="translate(-379.000000, -240.000000)"
                                        fill="currentColor"
                                    >
                                        <g
                                            id="icons"
                                            transform="translate(56.000000, 160.000000)"
                                        >
                                            <polygon
                                                id="plus-[#1512]"
                                                points="344 89 344 91 334.55 91 334.55 100 332.45 100 332.45 91 323 91 323 89 332.45 89 332.45 80 334.55 80 334.55 89"
                                            />
                                        </g>
                                    </g>
                                </g>
                            </g></svg
                        ></button
                    >
                    <div id="tools">
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
                </header>
                <div class="display">
                    <CodeMirror
                        bind:value
                        on:change={fileSize}
                        tabSize="4"
                        lang={python()}
                        theme={githubDark}
                        styles={{
                            "&": {
                                height: "82vh",
                                overflow: "auto",
                                backgroundColor: "var(--active-main) !important"
                            },
                            ".cm-gutters": {
                                backgroundColor: "var(--active-main)",
                                borderRight: "transparent",
                            },
                            ".cm-lineNumbers": { minWidth: "3.6vw" },
                            ".cm-foldGutter": { width: "1	vw" },
                            ".cm-wrap": { height: "100%" },
                            ".cm-scroller": { overflow: "auto" },
                            
                        }}
                    />
                    <button id="submit-button" on:click={submit}>
                        <p>Submit</p></button
                    >
                </div>
            </div>
            <div id="error_panel" class={show_info ? "v33" : ""}>
                <header>
                    <h4>
                        {tabs[active_tab]["errors"].length} issues in `{tabs[
                            active_tab
                        ]["name"].slice(0, -3)}`
                    </h4>
                </header>
                <div id="error_display" class="display">
                    <div class="group">
                        <div id="table_head">
                            <p>Code</p>
                            <p>Description</p>
                            <p>Category</p>
                        </div>
                        <div id="errors">
                            {#each tabs[active_tab]["errors"] as error}
                                <div
                                    class="error-row"
                                    on:click={() => highlight(error[0])}
                                >
                                    <div
                                        class="{error[2][0].toLowerCase()} error-code"
                                    >
                                        <div />
                                        <p>{error[2]}</p>
                                    </div>
                                    <div class="error-text">
                                        {error[3]}
                                    </div>
                                    <div><p>{categories[error[2]]}</p></div>
                                </div>
                            {/each}
                        </div>
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
</main>

<style lang="scss">
    $bg-colour: #151515;
    $br-colour: #242424;
    $sc-colour: #2a2c30;
    $icon-colour: #e4e9ee;
    $text-colour: #d3d7dc;
    $textsc-colour: #6b6d6f;

    ::selection {
        background-color: #0078d7 !important;
    }

    .error-row-display {
        font-family: "Segoe UI", sans-serif;
        color: var(--active-text);
        font-size: 14px;
        padding: 1% 1.6% 1% 4%;
        background-color: transparent;
        width: 100%;
        display: flex;
    }

    .error-row {
        p {
            margin: auto 0;
        }
    }

    .workspace-section {
        height: 6vh;
        display: flex;
        border-bottom: 1px solid $br-colour;
        padding-left: 4px;
    }

    .category-title {
        color: $text-colour;
        font-family: "Segoe UI", sans-serif;
        border-width: 1px 0px;
        gap: 2px;
        font-size: 14px;
        font-weight: 550;
        display: inline-flex;
        width: 100%;
        padding: 6px 4px;
        p {
            margin: auto 0;
        }
    }

    .reveal {
        display: flex;
        border: none;
        background-color: transparent;
        padding: 0;
        svg {
            color: $br-colour;
            width: 22px;
            margin: auto 0;
        }
    }

    .rev-right > svg {
        rotate: 0deg;
    }

    .rev-down > svg {
        rotate: 90deg;
    }

    #workspace-rules {
        border-bottom: 1px solid $br-colour;
        padding: 8px 0 12px 0;
    }

    #workspace-share {
        border-bottom: 1px solid $br-colour;
        display: inline-flex;
        flex-direction: column;
        width: 100%;
        gap: 4px;
        height: 20vh;

        div {
            width: 100%;
            display: flex;
            height: 4vh;
            color: $text-colour;

            button,
            input {
                color: $text-colour;
                margin: 0 12px;
                background-color: $br-colour;
                border: none;
                width: 100%;
                border-radius: 4px;
            }
        }

        div:first-child {
            margin-top: 16px;
        }

        p {
            margin: auto 12px;
            font-family: "Segoe UI", sans-serif;
            font-size: 14px;
        }
    }

    #workspace-info {
        height: 20vh;
        font-family: "Segoe UI", sans-serif;
        color: $text-colour;
        border-bottom: 1px solid $br-colour;

        ul {
            padding-left: 20px;

            div {
                width: 100%;
                display: inline-flex;
                gap: 7px;

                select {
                    padding: 0 6px;
                }
            }
        }

        p {
            font-size: 14.5px;
            margin: 4px 0;
        }
    }

    #lint-select {
        height: 30px;
        margin: auto 0;
        background-color: $bg-colour;
        border: $br-colour 1px solid;
        color: $text-colour;
        border-radius: 6px;
        share: $text-colour;
    }

    footer {
        width: 100%;
        display: inline-flex;

        p {
            margin: 0;
            font-family: "Segoe UI", sans-serif;
            color: $text-colour;
            font-size: smaller;
        }

        #footer_details {
            display: inline-flex;
            width: fit-content;
            margin-left: auto;

            p {
                margin-right: 12px;
            }
        }

        #footer_count {
            display: inline-flex;

            p {
                margin-left: 12px;
            }
        }
    }

    #editor {
        overflow: auto;

        header {
            display: inline-flex;
        }
    }

    h4 {
        font-family: "Segoe UI", sans-serif;
        color: $text-colour;
        font-size: 15px;
        font-weight: 600;
        width: fit-content;
        margin: auto 0;

        margin-left: 1%;
    }

    div.group {
        margin: 0 10px;
        height: 100%;
        overflow: auto;
    }

    .filename {
        font-family: Consolas, monospace;
        font-size: 16.5px;
    }

    header {
        height: 6vh;
        background-color: $bg-colour;
        display: flex;
    }

    div.display {
        height: 93%;
        width: 100%;
        position: relative;
    }

    button:hover {
        cursor: pointer;
    }

    #tab_menu {
        display: inline-flex;
        max-width: 100%;
        height: 100%;
    }

    .v33 {
        width: 33vw !important;
    }

    #tab_menu {
        overflow-x: auto;
    }

    .tab {
        border-bottom: 1px solid $br-colour;
        width: fit-content;
        display: inline-flex;
        padding-left: 16px;
        padding-bottom: 2px;
        border-right: 1px solid $br-colour;
        gap: 7px;

        button {
            width: fit-content;
            display: inline-flex;
            background-color: transparent;
            border: none;
            gap: 7px;
        }

        p {
            margin: auto;
            font-weight: 500;
            color: $text-colour;
            font-style: italic;
        }
    }

    .active-tab {
        border-bottom: none !important;
    }

    #tools {
        width: 100%;
        border-bottom: 1px solid $br-colour;
        border-left: 1px solid $br-colour;
        order: 4;
        display: inline-flex;
        gap: 7px;
        padding: 0 8px;

        button {
            border: none;
            background-color: transparent;
            color: $text-colour;

            p {
                margin: auto;
            }
        }
    }

    #add_tab {
        height: 100%;
        background-color: transparent;
        border: none;
        border-bottom: 1px solid $br-colour;
        padding: 0 8px;
        display: flex;
        flex: 1;
        max-width: 100%;

        svg {
            width: 0.9vw;
            margin-right: auto;
            display: block;
            color: $icon-colour;
        }
    }

    #tools {
        display: flex;
        width: fit-content;
    }

    .close {
        height: 100%;
        background-color: transparent;
        border: none;
        margin-right: 5px;
        padding-top: 2px;
        z-index: 10;
        svg {
            width: 1.5vw;
            margin: auto;
            display: block;
            color: $icon-colour;
        }
    }

    #info_panel {
        overflow-y: auto;
        overflow-x: hidden;
        z-index: 100;
        background-color: $bg-colour;
        height: 100%;
        flex-shrink: 0;
        width: 30%;
    }

    main {
        overflow-x: hidden;
        background-color: $br-colour;
        display: flex;
        flex-direction: column;
        width: 100vw;
        height: 100vh;
        gap: 1px;

        #header {
            height: 4vw;
            width: 100%;
            display: inline-flex;
            gap: 1px;

            #title {
                background-color: $bg-colour;
            }
            #logo {
                img {
                    width: 2.8vw;
                    height: 2.8vw;
                    background-color: $bg-colour;
                    margin: auto;
                    border-radius: 4px;
                }
                display: flex;
                width: 4vw;
                height: 4vw;
                background-color: $bg-colour;
            }

            #title {
                width: 100%;
                height: 100%;
                display: inline-flex;

                #git_path {
                    width: fit-content;
                    display: flex;
                    margin: auto auto auto 4%;
                    background-color: #2a2c30;
                    color: $text-colour;
                    border-radius: 6px;
                    padding: 3.5px 7px;
                }

                svg {
                    width: 1.6vw;
                    margin-right: 8px;
                }

                p {
                    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
                    font-size: 12.5px;
                    font-weight: 600;
                    margin: auto;
                }
            }
        }

        #body {
            height: 88%;
            width: 100%;
            display: inline-flex;
            gap: 1px;
            #menubar {
                width: 4vw;
                height: 100%;
                display: flex;
                flex-direction: column;
                gap: 1px;

                #app {
                    width: calc(4vw - 2px);
                    height: 100%;
                    background-color: $bg-colour;

                    button:first-child {
                        margin-top: 0.1vw;
                    }

                    button {
                        width: 100%;
                        height: 4vw;
                        background-color: transparent;
                        border: 0;
                        color: $icon-colour;

                        svg {
                            display: block;
                            margin: auto;
                            width: 1.85vw;
                        }
                    }
                }
            }

            #main {
                width: 100%;
                height: 100%;
                display: inline-flex;
                gap: 1px;

                #editor {
                    width: 100%;
                    display: inline-flex;
                    flex-direction: column;

                    #codemirror {
                        height: 60vh !important;
                    }
                }

                #error_panel {
                    width: 40%;
                    flex-shrink: 0;
                    height: 100%;
                    display: inline-flex;
                    flex-direction: column;
                    gap: 1px;

                    #error_display {
                        background-color: $bg-colour;
                        overflow-y: fixed;

                        .group {
                            #table_head {
                                display: grid;
                                grid-template-columns: 13% 65% auto;
                                border-bottom: 1px solid $br-colour;
                                background-color: $bg-colour;
                                width: 100%;
                                position: sticky;
                                top: 0;
                                z-index: 5;

                                p {
                                    font-size: 11px;
                                    color: $textsc-colour;
                                    font-family: "Segoe UI", sans-serif;
                                    margin: 9px 0 3px 4px;
                                    font-weight: 700;
                                }
                            }

                            #errors {
                                overflow-y: auto;
                                position: inline-flex;
                                flex-direction: column;
                            }
                        }
                    }
                }
            }
        }
    }

    :global(.CodeMirror-selected) {
        background-color: #ff0000 !important; /* Change this to your desired color */
    }
</style>
