# Task 4: Web Application Automation Code Review & Refactoring Rationale

## 1. Code Review Feedback Memo
**To:** Junior QA Automation Engineer  
**From:** Quality Assurance Lead  
**Subject:** Code Review & Refactoring Guidance: Escher Map Loader E2E Test Spec  

Hi! Thank you for drafting the initial automated test path for our Escher map ingestion feature. Your script correctly captures the core user milestones, but we need to address three major architectural anti-patterns before this code can merge:

1.  **Eliminate Hardcoded Static Waits:** Using `page.waitForTimeout(5000)` introduces mandatory delays that slow down automated build runners and can hide timing bugs. We must replace these with dynamic, state-aware locator assertions.
2.  **Scrub Fragile DOM Selectors:** Referencing strict layout positions like `div.menu-button:nth-child(2)` breaks immediately upon minor UI style updates or structural shifts. We should prioritize user-visible, accessible text elements or explicit data-attributes instead.
3.  **Introduce Verification Assertions:** Your script currently logs a generic string (`console.log('Map loaded')`) without performing any validation checks on the page. A test without an assertion isn't testing anything—we need to verify that graph nodes actually render on the SVG canvas.

## 2. Playwright Core Refactoring Framework
*   **The Page Object abstraction:** All raw DOM query configurations have been extracted into `EscherViewerPage.ts`. This encapsulates application-specific quirks—such as Escher utilizing custom text markers instead of standard HTML disabled attributes—keeping our individual test specs clean and maintainable.
*   **SVG-Safe Text Extractions:** Switched from `allInnerTexts()` to `allTextContents()`. Because Escher renders components inside an SVG canvas layer, standard HTML inner text lookups return undefined, whereas text contents parse node vectors perfectly.