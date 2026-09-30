# CORVUS DEV CONTEXT RULES

When constructing context for the local development model:

1. Include the user's development request.
2. Include relevant architecture facts.
3. Include only relevant source files or excerpts.
4. Include relevant runtime/test output.
5. Label every source with its real path.
6. Separate source evidence from instructions.
7. Never include secrets automatically.
8. Never claim unseen source was inspected.
9. Prefer retrieval over dumping the entire repository.
10. Keep context within the model's usable context window.

The current local model is small.

Therefore CORVUS should retrieve a small number of highly relevant files rather than flooding the model with the entire project.
