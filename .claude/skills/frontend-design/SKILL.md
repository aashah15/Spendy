---
name: spendy-ui-designer
description: >
  Generates modern, production-ready UI components and pages for Spendy — a
  personal expense tracker built with Flask/Jinja2 + vanilla CSS
  (https://github.com/aashah15/Spendy). Always triggers when the user asks to
  design, create, build, improve, or redesign any page or component for Spendy
  or any expense/finance tracker UI. Trigger on phrases like "design the ___ page",
  "create UI for ___", "build a component for ___", "redesign ___", "improve the
  layout of ___", even if the user doesn't say "Spendy" explicitly. Output is
  clean Jinja2 HTML + vanilla CSS matching the existing project style. Never
  produce generic or boilerplate UI — always aim for a polished, modern fintech look.
---

# Spendy UI Designer

Generates production-ready Jinja2 templates and vanilla CSS for the Spendy expense tracker.

## Repo

https://github.com/aashah15/Spendy  
Stack: **Flask + Jinja2** (templates/) + **Vanilla CSS** (static/) — no React, no Tailwind.

---

## Step 1: Fetch the existing design (always do this first)

Before writing any code, fetch the live CSS so your output matches the real project:

```
web_fetch: https://raw.githubusercontent.com/aashah15/Spendy/main/static/style.css
```

Also fetch at least one existing template for structural context:

```
web_fetch: https://raw.githubusercontent.com/aashah15/Spendy/main/templates/base.html
web_fetch: https://raw.githubusercontent.com/aashah15/Spendy/main/templates/dashboard.html  (or index.html)
```

If a fetch fails (404), try common template names: `index.html`, `layout.html`, `expenses.html`.

**If fetches fail entirely** — ask the user to paste their `style.css` or a screenshot of the existing UI before proceeding.

Once you have the CSS: extract the color palette, font choices, spacing scale, card/button/input patterns, and any CSS custom properties. Use these as your strict design tokens going forward.

---

## Step 2: Clarify the request (if needed)

If the user's request is ambiguous, ask ONE focused question before starting. Examples:
- "Which page — the list view or a detail view?"
- "Should this component be a modal or an inline form?"
- "What data fields does this section need to show?"

If the request is clear enough, skip this and proceed.

---

## Step 3: Plan the UI (brief, in prose)

Before writing code, describe:
1. **Layout** — page structure (sidebar, topbar, main content area, etc.)
2. **Key sections** — what cards/panels/tables/forms appear and why
3. **UX decisions** — any non-obvious choices (e.g. "amounts use color-coded badges for income vs expense")

Keep this to 5–8 lines. It's a checkpoint for the user, not a spec doc.

---

## Step 4: Generate the code

### Output rules

- **Jinja2 HTML**: extend `base.html` with `{% extends "base.html" %}` and fill `{% block content %}`. Use Jinja2 template syntax for dynamic data (`{{ expense.amount }}`, `{% for e in expenses %}`).
- **CSS**: write a `<style>` block inside the template OR a dedicated `.css` file if the component is large. Never use inline styles except for truly dynamic values (e.g. progress bar width).
- **Icons**: use [Lucide Icons](https://lucide.dev) via CDN (`<script src="https://unpkg.com/lucide@latest"></script>`) or inline SVG. Heroicons are also acceptable. Always prefer icons over emoji.
- **No external frameworks**: no Bootstrap, Tailwind, React, or jQuery. Vanilla CSS + vanilla JS only.
- **Modular**: each component/page is a self-contained template or include. Avoid copy-pasting the same CSS across files — extract reusables into `static/style.css`.

### Design rules (enforce strictly)

| Rule | Detail |
|---|---|
| Color palette | Match exactly from fetched CSS. If no palette found, use: `--primary: #6366f1`, `--bg: #f8fafc`, `--surface: #ffffff`, `--text: #1e293b`, `--muted: #64748b`, `--danger: #ef4444`, `--success: #22c55e` |
| Spacing | 8px grid — use multiples of 8 for all padding/margin/gap |
| Cards | `border-radius: 12px`, `box-shadow: 0 1px 3px rgba(0,0,0,0.08)`, `padding: 24px` |
| Typography | Clean sans-serif (match existing). Hierarchy: 24px page title → 16px body → 13px meta/labels |
| Inputs & buttons | Rounded (`border-radius: 8px`), clear focus states, no sharp edges |
| Amounts | Color-code: expenses in `--danger`, income in `--success`, neutral in `--text` |
| Empty states | Always include a friendly empty state (icon + message) for lists/tables |
| Responsive | Mobile-first. Use CSS Grid or Flexbox. No fixed pixel widths on containers. |

### Anti-patterns — never do these

- ❌ Generic gray boxes with no visual hierarchy
- ❌ Unthemed default browser form styles
- ❌ Walls of unstyled `<table>` rows
- ❌ Hardcoded colors that don't match the palette
- ❌ Missing hover/focus states on interactive elements
- ❌ No loading or empty states

---

## Step 5: Deliver the output

Default: show the code inline in chat as an artifact (HTML + CSS in a single code block or two clearly labelled blocks).

If the user says "save it", "download it", or "write it to a file" — create the file at the appropriate path:
- Templates → `templates/<name>.html`
- Styles → `static/<name>.css`

Always end with a short note on:
- What Jinja2 variables the template expects (e.g. `expenses: list[Expense]`)
- Any Flask route changes needed to pass that data
- Any new CSS classes added to `style.css`

---

## Quick reference: common Spendy pages

| Page | Key elements |
|---|---|
| Dashboard | Summary cards (total spend, budget left, top category), recent transactions list, spending chart |
| Expenses list | Filterable table/card list, category badges, amount column, add button |
| Add/Edit expense | Form with amount, category, date, note fields, submit + cancel |
| Categories | Category cards with color swatch, icon, spend total, edit/delete actions |
| Reports/Analytics | Bar/line chart, breakdown by category, date range picker |
| Settings | Profile section, budget settings, currency preference |

---

## Notes

- The skill fetches the repo at task time — always use live CSS, not memory.
- If the user provides screenshots of the existing UI, prioritize those over fetched CSS for visual matching.
- If asked to redesign from scratch (ignoring existing style), confirm with the user first before deviating from the project's look.