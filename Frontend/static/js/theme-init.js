// Runs before the page is drawn, so the saved theme shows without a flash of the wrong colours.
(function () {
  var theme = null;
  try { theme = localStorage.getItem("denpointment-theme"); } catch (error) { /* storage can be blocked */ }
  if (theme !== "light" && theme !== "dark") {
    theme = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  document.documentElement.setAttribute("data-theme", theme);
})();
