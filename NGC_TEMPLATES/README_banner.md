> **NGC = research repo.** No production code here.
> - **Data spec + validator:** lives in **GAP** → https://github.com/ShagaDAO/gap  
> - **Wire protocol + validator:** lives in **DGN** → https://github.com/ShagaDAO/dgn  
> - **NGC's job:** explore neural game codecs that *consume GAP data* and *could emit DGN frames* in future.

## How the repos fit (one view)

GAP (frames+controls spec) ➜ [validated shards] ➜ NGC (research: train/eval codecs) ➜ DGN (protocol: SemanticUpdate + ResidualChunk)

- **GAP → NGC:** NGC experiments assume GAP v0.x shards (video + controls JSONL).
- **NGC → DGN (future):** When we prototype, we'll export "SemanticUpdate/ResidualChunk" *samples* that conform to DGN's schemas for analysis. 