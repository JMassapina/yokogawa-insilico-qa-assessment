# ADR-0003: Target Public Environment Path Mapping

## Status
Accepted

## Context
The Escher single-page metabolic network visualization canvas relies on heavily nested layout coordinate systems and external font vector definitions. Attempting to bundle and serve these scripts locally inside resource-constrained GitHub Action containers introduces background execution sandboxing errors that lead to pipeline timeout flakes.

## Decision
We decouple the infrastructure layer by pointing our active Playwright runner configurations directly at the production sub-directory route (`https://github.io`). 

## Consequences
By bypassing local server overhead, the pipeline tests run with maximum execution fidelity and clean processing speeds. To insulate the suite against unexpected upstream changes, our test specifications leverage robust accessible role text locators that adapt dynamically to canvas updates.