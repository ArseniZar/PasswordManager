export function attachPasswordEntryHandlers() {
  document.querySelectorAll(".password-entry").forEach(entry => {
    entry.addEventListener("click", (e) => {
      if (
        e.target.classList.contains("password-checkbox") ||
        e.target.classList.contains("edit-btn")
      ) return;

      const details = entry?.parentElement?.querySelector(".details");
      if (details) details.classList.toggle("hidden");
    });
  });
}
