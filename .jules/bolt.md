## 2024-05-18 - Optimize skill validator dependency sorting
**Learning:** Found an O(V³) worst-case bottleneck in `tools/skill_validator.py` due to nested loops and inefficient queue sorting on graph algorithms. Using `heapq` and adjacency lists optimizes Kahn's topological sort to O(V log V + E) for alphabetical node processing.
**Action:** When implementing topological sort or graph processing with alphabetical tie breaking requirements, avoid standard list sorts inside while loops and use a min-heap structure (`heapq`) along with proper dependency mappings.
## 2024-05-19 - Duplicate File I/O Optimization in Skill Validator
**Learning:** In codebases where files are repeatedly parsed (like Markdown frontmatter and full-text searches), redundant `file.read_text()` operations can significantly slow down execution when processing many files.
**Action:** When a file parsing function successfully reads the raw content of a file, refactor it to return that raw content alongside its parsed structures, so downstream steps can reuse the text rather than reading from disk again.
