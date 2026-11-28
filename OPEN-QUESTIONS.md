# Open questions

Questions about private-cloud-manager only, for the author (DESIGN-23 in the workspace's [system design](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/spec/design/system.md)). A question that binds several repositories goes to the workspace's [OPEN-QUESTIONS.md](https://github.com/e1-rahabok/private-cloud-workspace/blob/main/OPEN-QUESTIONS.md). IDs are `Q-PCM-n` (DESIGN-23). Write the reply after `Answer:`.

### Q-PCM-5 Does the public demo answer questions with Agent E2?

The public demo ([R-PUBLIC-001](spec/requirements/public-demo.md)) is open to anyone. Agent E2's answers cost money on every question, and an open endpoint can be abused.

- Should a visitor of the public demo be able to ask Agent E2 a question, or see only the explanations the synthetic demo already holds?
- **Working assumption:** only the stored explanations; no live question to Agent E2. The spec and build go on with this.

Answer:
