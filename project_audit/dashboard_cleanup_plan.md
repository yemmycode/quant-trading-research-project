# Dashboard Cleanup Plan

## Purpose

This document records how the Streamlit dashboard should be cleaned and reorganized during the consolidation phase.

The priority is to avoid breaking app.py while gradually moving toward a clean user experience.

---

## Current Approach

The dashboard currently has many useful sections, but they are scattered.

We will not physically move large blocks yet. Instead, we will:

```text
1. Add a Dashboard Structure Guide
2. Keep Trading Control Center as the main workflow
3. Treat other sections as support panels
4. Use syntax checks after every app.py change
5. Move sections physically only after the app is stable
```

---

## Target Dashboard Groups

```text
1. Trading Control Center
2. Portfolio & Orders
3. Safety & Readiness
4. System Admin
5. Documentation & Architecture
```

---

## Rule Going Forward

Do not add new feature panels unless they directly support the consolidated paper-trading workflow.

The next major development should focus on connecting existing modules, not adding random new modules.