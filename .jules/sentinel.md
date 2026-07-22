## 2026-07-22 - [Insecure Default File Permissions for Agent Logs]
**Vulnerability:** Agent logs and history files were being created with default system permissions (often world-readable), which could expose sensitive data like API keys, secrets, or internal context stored in the logs.
**Learning:** System-generated logs often contain highly sensitive data implicitly. Failing to explicitly secure file creation leads to passive data leakage, bypassing application-level security boundaries.
**Prevention:** Always enforce strict POSIX file permissions (`0o600` for files, `0o700` for directories) when writing logs or caches programmatically.

## 2026-07-22 - [Config and Prompt File Exposure during Hot-Reloading]
**Vulnerability:** Programmatic updates to agent configurations, system prompts, reasoning traces, and versioned skill files can be exposed to unauthorized local users if created with standard world-readable permissions.
**Learning:** Config files and prompts often govern the security posture and operational boundaries of an agent. Exposing them can allow local privilege escalation or prompt injection attacks.
**Prevention:** Enforce strict `0o600` POSIX file permissions programmatically using `os.open` with specific O_CREAT flags when updating prompts, configurations, or reasoning trace files during evolution cycles.
