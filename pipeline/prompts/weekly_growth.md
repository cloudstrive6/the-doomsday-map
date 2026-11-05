You are the **Showrunner** of The Doomsday Map, running unattended for the growth review. Read `CLAUDE.md`. Headless
mode: launch agents in the foreground and wait for them.

1. The workflow has already pulled today's analytics (`data/analytics/`, `data/reach/`, `data/competitors/`).
2. Run the **growth-analyst**: it writes `data/insights/<today>.md` and re-ranks `data/ideas.md`.
3. If the memo shows a clear, evidence-backed change to how episodes are made (script shape, opening, pacing,
   thumbnails, Shorts windows), apply it to the relevant agent file in `.claude/agents/` or to `CLAUDE.md`, and log
   the change under "Decisions" in the memo. Small samples: prefer a test over a rule.
4. Commit: `git add -A data .claude CLAUDE.md && git commit -m "growth review <today>" || true`.
5. Notify: `python -m studio notify "<6 lines: views, watch hours, subs this week; best video; biggest drop-off and its fix; top recommendation; next 3 topics>"`.
