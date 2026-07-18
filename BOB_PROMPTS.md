# IBM Bob Prompts

Open the project folder in IBM Bob IDE, switch to **Code mode**, and run `/init` once.
Then use the tasks below one at a time.

## Task 1 — Verify the project

```text
Read AGENTS.md and inspect the complete repository. Create a virtual environment, install requirements, train the model, run all tests, and start the FastAPI application. Fix only real errors. Do not remove safety warnings or input validation. Report the commands run and the final local URL.
```

## Task 2 — Improve the dataset safely

```text
Expand data/training_emails.csv with balanced, clearly fictional phishing and legitimate examples. Avoid real credentials, personal information, live malicious links, or copyrighted email content. Retrain the model, compare validation metrics, and add tests that protect existing API behavior.
```

## Task 3 — Review the code

```text
Review this repository for security, privacy, correctness, and maintainability. Prioritize unsafe logging, unvalidated input, secret exposure, dependency risks, weak tests, and misleading model claims. Apply low-risk fixes and run pytest -q afterward.
```

## Task 4 — Prepare a GitHub release

```text
Check README accuracy, verify screenshots and setup commands, run tests, and produce a concise release checklist. Do not claim an IBM certificate exists. Flag any missing evidence that must be supplied by the project owner.
```
