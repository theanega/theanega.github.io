(function () {
  var STORAGE_KEY = "theme-preference";

  function getStoredTheme() {
    try {
      return localStorage.getItem(STORAGE_KEY);
    } catch (_) {
      return null;
    }
  }

  function setStoredTheme(value) {
    try {
      localStorage.setItem(STORAGE_KEY, value);
    } catch (_) {}
  }

  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
  }

  function initToggle() {
    var btn = document.querySelector("[data-theme-toggle]");
    if (!btn) return;

    function syncLabel() {
      var theme = document.documentElement.getAttribute("data-theme") || "light";
      btn.setAttribute(
        "aria-label",
        theme === "dark" ? "Switch to light mode" : "Switch to dark mode"
      );
    }

    btn.addEventListener("click", function () {
      var current = document.documentElement.getAttribute("data-theme") || "light";
      var next = current === "dark" ? "light" : "dark";
      applyTheme(next);
      setStoredTheme(next);
      syncLabel();
    });

    syncLabel();

    window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", function (e) {
      if (getStoredTheme()) return;
      applyTheme(e.matches ? "dark" : "light");
      syncLabel();
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initToggle);
  } else {
    initToggle();
  }
})();
