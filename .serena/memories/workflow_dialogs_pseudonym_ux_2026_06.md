# Workflow/dialog UX decisions from 2026-06 work

- The LLM-generation dialog should favor readability over framed decoration. Remove unnecessary dialog/frame styling, improve wording, and use a clear divider before the step chooser (`Choose the step (1-4) you want to work on now.` or localized equivalent).
- In dark mode, dialog headings and body text need explicit contrast checks; avoid muted heading colors that become hard to read.
- Pseudonym reservation should be guided as a complete workflow: reserve pseudonym, enter and confirm the recovery secret, explain what the secret is for, and support re-login with a reserved pseudonym without relying on hidden assumptions.
- Recovery secrets must not be treated like recoverable plaintext. UX can confirm matching entry at creation time, but storage/verification should remain hash-based and avoid exposing the secret later.
- Keep pseudonym/reservation language concrete and student-friendly; avoid technical account-management jargon where possible.