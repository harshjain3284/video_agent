# 🛡️ Development Priorities: Stability First

This document outlines the core philoshopy for the Video Agent development.

## 1. Stability over Features
The project is currently in a functional state. No new features should be implemented if they risk breaking the core pipeline. 

## 2. No Breaking Changes
- Before renaming or moving any file, every import in the project must be verified.
- Any change to function signatures must be updated across all nodes.

## 3. "Safety Net" Coding
- Every AI node must use `try-except` blocks.
- Every node must have a "Fallback" mechanism (e.g., if AI video fails, use Image animation).
- The pipeline should **NEVER** crash; it should always produce a result, even if it's a fallback.

## 4. Careful Refactoring
- Logic should be moved to `utils/` only when it is truly repetitive.
- Keep the `app.py` and `workflow.py` synchronized with internal node labels at all times.

---
**Current Status:** Working / Stable
**Priority Level:** CRITICAL ⚡
