# ClinicMS UI Design System & Frontend Guidelines

When implementing frontend components, views, or new layouts within the ClinicMS system, you **MUST STICK STRICTLY** to the established design system tokens provided through Tailwind CSS and Alpine.js.

## Tech Stack
- **Styling framework:** Tailwind CSS (via inline CDN configuration in `base.html`)
- **Interactivity:** Alpine.js (for tooltips, sidebars, dropdowns, and client-side toggles)

---

## 1. Color System (Tailwind Tokens)
We use an extended Tailwind CSS specification. **Do not use arbitrary colors.** Always stick strictly to these tokens:

- **Primary Brand:** `bg-primary`, `text-primary`, `border-primary` (`#0f766e` / Teal 700 tone). Use this for main call-to-actions, active highlights, and important icons.
- **Secondary / Heavy Text:** `text-slate-900` (mapped closely to `#0f172a `) for primary headings and strong titles.
- **Muted Elements:** `text-slate-500` or `text-slate-400` for eyebrows, breadcrumbs, subtitles, and placeholder-style descriptors.
- **Backgrounds:** 
  - `bg-slate-50` (`#f8fafc`) for main layout and page wrappers.
  - `bg-white` (`#ffffff`) for elevated panels, cards, and primary surfaces.
- **Feedback & States:** `danger` (Red/Rose), `success` (Green), `warning` (Amber). For example: A logout button typically merges a `bg-rose-50` plate with `text-rose-600` font.

---

## 2. Radii and Shadows (The "Softness" Aesthetic)
The ClinicMS design mandates highly curved borders and very soft, widely dispersed drop-shadows.

- **Global Shadows:** DO NOT use native `shadow-md` or `shadow-lg`. We have heavily configured custom shadows:
  - `shadow-soft`: Default elevation for components (cards, standard buttons).
  - `shadow-panel`: Heavy elevation for floating elements like dropdowns or large modal layers.
- **Border Radius:** Do not use `rounded`, `rounded-md`, or raw sharp corners. 
  - Standard interactive elements (buttons, inputs, links) must use `rounded-2xl` or `rounded-xl`.
  - Main cards and larger layout panels must use our custom utility `rounded-panel` (which maps to `1.5rem` or `24px`) or `rounded-3xl`.

---

## 3. UI Component Examples

### Typical Card/Panel Layout:
```html
<div class="rounded-panel border border-slate-200 bg-white p-6 shadow-soft">
    <!-- Panel Content -->
</div>
```

### Form Inputs
All form inputs heavily favor spacious padding, 2xl radii, and interactive focus states with custom rings.
```html
<input 
    type="text" 
    placeholder="Enter data" 
    class="h-11 w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 text-sm outline-none transition focus:border-primary focus:bg-white focus:ring-4 focus:ring-teal-50"
>
```

### Buttons
All buttons must have a layout transition mapped through Tailwind logic:
- **Primary Action (Form submission/Save):** 
  ```html
  <button class="inline-flex h-10 items-center justify-center rounded-2xl bg-primary px-4 py-2 text-sm font-medium text-white shadow-soft transition hover:opacity-90">
      Save Patient
  </button>
  ```
- **Secondary Action (Cancel/Links):** 
  ```html
  <button class="inline-flex h-10 items-center justify-center rounded-2xl bg-white px-4 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-50 hover:text-slate-900 border border-slate-200">
      Cancel
  </button>
  ```
- **Sidebar Selection Logic:** If building navigation components, the active route uses `bg-primary text-white shadow-soft` while the inactive routes use `text-slate-600 hover:bg-white hover:text-slate-900`.

### Typography hierarchy
- **Page Titles**: Usually left-aligned `text-xl font-semibold tracking-tight text-slate-900`. 
- **Section Headers** (Eyebrow labels): Use `text-xs font-semibold uppercase tracking-[0.2em] text-slate-400`.

---

## 4. Javascript and Interactivity (Alpine.js)
Since the project relies solely on **Alpine.js**, do not implement heavy Vanilla JS setups unless strictly required. 

Instead, construct toggle states inline:
```html
<!-- Interactive dropdown example -->
<div x-data="{ open: false }" class="relative">
    <button @click="open = !open">Toggle</button>
    
    <div x-cloak x-show="open" x-transition class="absolute shadow-panel rounded-3xl bg-white">
        <!-- Content -->
    </div>
</div>
```
Always use `x-cloak` to prevent elements from flashing before Alpine initializes.
