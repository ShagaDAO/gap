## Toy pass-through (offline)
This repo is **research only**. To make the "GAP → NGC → DGN" flow concrete, we include two **DGN‑shaped sample files**:

- `samples/dgn/semantic_update.jsonl`
- `samples/dgn/residual_chunk.json`

They are schema-only examples (static), so DGN's validator can confirm the wire format:
```bash
# from the DGN repo
python3 tools/validator/cli.py check --schema dgn-semantic-update-0.1.0.json <path>/ngc/samples/dgn/semantic_update.jsonl
python3 tools/validator/cli.py check --schema dgn-residual-chunk-0.1.0.json <path>/ngc/samples/dgn/residual_chunk.json
```

### Compatibility
| Producer | Consumer | Status |
|---|---|---|
| GAP v0.2.x shard | NGC notebooks/tools (research) | ✅ supported (toy) |
| NGC DGN‑shaped samples | DGN validator | ✅ passes schemas |
| DGN 0.1.0 schemas | DGN validator | ✅ CI enforced | 