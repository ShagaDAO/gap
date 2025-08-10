## Two‑minute tour (validator)
Validate our own samples:
```bash
python3 tools/validator/cli.py check --schema dgn-session-hello-0.1.0.json protocol/samples/session_hello.json
python3 tools/validator/cli.py check --schema dgn-semantic-update-0.1.0.json protocol/samples/semantic_update.jsonl
python3 tools/validator/cli.py check --schema dgn-residual-chunk-0.1.0.json protocol/samples/residual_chunk.json
```
Validate the **NGC** toy outputs (offline):
```bash
python3 tools/validator/cli.py check --schema dgn-semantic-update-0.1.0.json ../ngc/samples/dgn/semantic_update.jsonl
python3 tools/validator/cli.py check --schema dgn-residual-chunk-0.1.0.json ../ngc/samples/dgn/residual_chunk.json
```

### Compatibility
| Producer | Consumer | Status |
|---|---|---|
| GAP v0.2.x shard | NGC notebooks/tools (research) | ✅ supported (toy) |
| NGC DGN‑shaped samples | DGN validator | ✅ passes schemas |
| DGN 0.1.0 schemas | DGN validator | ✅ CI enforced | 