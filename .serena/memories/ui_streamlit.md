# UI and Streamlit conventions

- UI text is German, short, direct, and suited to media-affine learners without IT prerequisites.
- Streamlit 1.58 conventions: use `width="stretch"` / `width="content"`; avoid `use_container_width`; use `st.html`/`st.iframe`; avoid new `st.components.v1.html`.
- Never nest `st.expander` blocks. Keep widget keys unique and stable, especially repeated navigation, bookmark, jump, export, and answer-option controls.
- Keep vertical margins compact but not cramped. Button labels must remain vertically centered. Header, question stem, and answer options should fit without overlap on mobile and desktop.
- On mobile, avoid triggering the virtual keyboard for read-only or non-editable controls.
- Active tests should protect against accidental page reloads with `beforeunload` where possible. Browser-supplied warning dialogs cannot reliably use custom text.
- Timer, pacer, and warning hints must match the currently visible remaining time. Avoid stale warnings that update only after changing questions. Rounding should not contradict the displayed timer.
- Dark theme contrast must be readable. Do not add heavy borders/background panels unless a design problem requires it.
- Prompt preview should render Markdown safely and read-only; raw copy/download remains the authoritative way to transfer prompts.