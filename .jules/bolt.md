## 2024-05-18 - Optimize skill validator dependency sorting
**Learning:** Found an O(V³) worst-case bottleneck in `tools/skill_validator.py` due to nested loops and inefficient queue sorting on graph algorithms. Using `heapq` and adjacency lists optimizes Kahn's topological sort to O(V log V + E) for alphabetical node processing.
**Action:** When implementing topological sort or graph processing with alphabetical tie breaking requirements, avoid standard list sorts inside while loops and use a min-heap structure (`heapq`) along with proper dependency mappings.
