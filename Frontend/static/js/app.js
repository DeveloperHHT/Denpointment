// Small behaviours of the interface: theme, mobile menu, toasts, confirm dialog.
(function () {
  "use strict";
  var root = document.documentElement;

  // ---- Theme ----
  function setTheme(theme) {
    root.setAttribute("data-theme", theme);
    try { localStorage.setItem("denpointment-theme", theme); } catch (error) { /* ignore */ }
    document.querySelectorAll("[data-theme-toggle]").forEach(function (button) {
      button.setAttribute("aria-pressed", String(theme === "dark"));
    });
  }
  document.querySelectorAll("[data-theme-toggle]").forEach(function (button) {
    button.setAttribute("aria-pressed", String(root.getAttribute("data-theme") === "dark"));
    button.addEventListener("click", function () {
      setTheme(root.getAttribute("data-theme") === "dark" ? "light" : "dark");
    });
  });

  // ---- Mobile menu ----
  var body = document.body;
  var scrim = null;
  function closeMenu() {
    body.classList.remove("menu-open");
    if (scrim) { scrim.remove(); scrim = null; }
  }
  function openMenu() {
    body.classList.add("menu-open");
    scrim = document.createElement("div");
    scrim.className = "scrim";
    scrim.addEventListener("click", closeMenu);
    body.appendChild(scrim);
  }
  document.querySelectorAll("[data-menu-toggle]").forEach(function (button) {
    button.addEventListener("click", function () { body.classList.contains("menu-open") ? closeMenu() : openMenu(); });
  });
  document.addEventListener("keydown", function (event) { if (event.key === "Escape") closeMenu(); });

  // ---- Toasts disappear by themselves ----
  function dismiss(toast) {
    toast.classList.add("leaving");
    setTimeout(function () { toast.remove(); }, 380);
  }
  document.querySelectorAll(".toast").forEach(function (toast, index) {
    var close = toast.querySelector("button");
    if (close) close.addEventListener("click", function () { dismiss(toast); });
    if (!toast.classList.contains("danger")) setTimeout(function () { dismiss(toast); }, 5200 + index * 500);
  });

  // ---- Confirm before destructive actions: <form data-confirm="Delete this address?"> ----
  var dialog = document.getElementById("confirm-dialog");
  var pending = null;
  if (dialog && typeof dialog.showModal === "function") {
    document.querySelectorAll("form[data-confirm]").forEach(function (form) {
      form.addEventListener("submit", function (event) {
        if (form.dataset.confirmed === "1") return;
        event.preventDefault();
        pending = form;
        dialog.querySelector("[data-confirm-text]").textContent = form.dataset.confirm;
        dialog.showModal();
      });
    });
    dialog.querySelector("[data-confirm-yes]").addEventListener("click", function () {
      dialog.close();
      if (pending) { pending.dataset.confirmed = "1"; pending.submit(); }
    });
    dialog.querySelector("[data-confirm-no]").addEventListener("click", function () { dialog.close(); pending = null; });
  }
})();

// Tables: copy the column titles into the cells, so the narrow-screen layout can show them as labels.
document.querySelectorAll(".table").forEach(function (table) {
  var titles = Array.prototype.map.call(table.querySelectorAll("thead th"), function (th) { return th.textContent.trim(); });
  table.querySelectorAll("tbody tr").forEach(function (row) {
    Array.prototype.forEach.call(row.children, function (cell, index) { cell.setAttribute("data-label", titles[index] || ""); });
  });
});
