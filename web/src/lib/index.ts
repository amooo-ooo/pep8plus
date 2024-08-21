// place files you want to import through the `$lib` alias in this folder.

import { writable } from "svelte/store"

export const files = writable({
    0: { title: "Untitled", content: "", errors: [] },
})
export const workspaces = {} // usually a multidimensional array
export const exp = writable({ tabs: [0], settings: {}, current_tab: 0 }) // experimental


export const errors = writable([])