# A deduplication helper that preserves the requested order

```python
def unique_ids(ids):
    return list(dict.fromkeys(ids))
```

**Supported improvement.** This returns a new list, keeps the first occurrence order for string IDs, and leaves the input unchanged. The old `sorted(set(ids))` explicitly sorted the IDs, so `["b", "a", "b"]` became `["a", "b"]` instead of `["b", "a"]`.

The user's later correction makes this an ongoing, concrete defect worth revisiting. Source: [synthetic conversation](history.md). Python 3.9 dictionaries preserve insertion order. The repository's demonstration regression test executes both functions and checks empty input, single/repeated IDs, mixed order, a new output list, and input immutability.

No live project was edited. Coverage: one synthetic conversation, one function. This is an authored demonstration with an automated regression check, not an independent model or human-usefulness evaluation.
