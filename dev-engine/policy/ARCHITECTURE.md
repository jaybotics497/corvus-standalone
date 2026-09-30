# CORVUS DEVELOPMENT ARCHITECTURE

PRODUCTION
~/corvus

DEVELOPMENT
~/corvus-dev

DEVELOPMENT COMPONENTS

policy/
    Development rules and safety boundaries.

staging/
    Candidate implementations before production promotion.

tests/
    Deterministic validation.

patches/
    Proposed and approved patches.

reports/
    Inspection, diagnosis and validation reports.


TARGET DEVELOPMENT FLOW

User request
    |
    v
DEV Router
    |
    v
Source Selector
    |
    v
Read-only Inspection
    |
    v
Local Model Reasoning
    |
    v
Patch Proposal
    |
    v
Deterministic Validator
    |
    v
Staging
    |
    v
Approval Gate
    |
    v
Production Promotion
    |
    v
Production Verification
    |
    +---- failure ----> Rollback


DESIGN PRINCIPLE

The model is the reasoning component.

The model is not the source of truth.

Filesystem state, source code, tests and runtime results are the source of truth.
