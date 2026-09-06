# 🎯 Recorded Escher Application DOM Baseline & Query Selectors

To ensure our automated browser suites rely on absolute truth rather than guessed paths, this log documents the verified DOM layout elements read directly from a running instance of `escher@1.8.2`.

---

##  ul.menu-bar Structure Index
The application navigation shell initializes using a standard flat container item matrix:

```html
<ul class="menu-bar">
  <li class="dropdown">
    <div class="dropdownButton">Map</div>
    <ul class="menu">
      <li class="menuButton"><label>Load map JSON<input type="file"></label></li>
      <li class="menuButton" id="disabled" tabindex="-1">Clear map</li>
    </ul>
  </li>
  <li class="dropdown">
    <div class="dropdownButton">Data</div>
    <ul class="menu">
      <li class="menuButton"><label>Load reaction data JSON<input type="file"></label></li>
      <!-- DEFECT ESC-01: id="disabled" remains locked after data file ingestion -->
      <li class="menuButton" id="disabled" tabindex="-1">Clear reaction data</li>
    </ul>
  </li>
</ul>
```

---

## 🛠️ Critical Selector Abstraction Rules

*   **Menu Group Resolution Mapping:** Target top-level containers using text criteria: `ul.menu-bar > li.dropdown`. Filter items via accessible regex selectors targeting `div.dropdownButton`.
*   **File Chooser File Injection Targets:** Direct action calls do not use high-overhead, race-prone file chooser event hooks. Target the hidden input elements nested behind label containers directly: `label.menuButton > input[type="file"]`. This approach simplifies the execution loop and removes pipeline timing noise.
*   **SVG Component Selections:** Target map lines and metadata groups using raw element classes: reactions render under `g.reaction`, node entities sit inside `g.node`, and path indicators use `path.segment`. Text nodes match `text.reaction-label`.
