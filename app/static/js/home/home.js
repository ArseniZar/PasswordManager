document.addEventListener("DOMContentLoaded", () => {
  const deleteBtn = document.getElementById("delete-selected-btn");
  const passwordsList = document.getElementById("passwords-list");
  const searchInput = document.getElementById("search");

  init();

  function init() {
    attachPasswordEntryHandlers();
    attachCheckboxHandlers();
    attachSearchHandler();
    attachDeleteHandler();
    updateDeleteBtnVisibility();
  }

  // === Обработчики кликов по записям паролей ===
  function attachPasswordEntryHandlers() {
    document.querySelectorAll(".password-entry").forEach((entry) => {
      entry.addEventListener("click", (e) => {
        if (
          e.target.classList.contains("password-checkbox") ||
          e.target.classList.contains("edit-btn")
        ) return;

        const details = entry.parentElement.querySelector(".details");
        if (details) details.classList.toggle("hidden");
      });
    });
  }

  // === Обработчики чекбоксов ===
  function attachCheckboxHandlers() {
    document.querySelectorAll(".password-checkbox").forEach((checkbox) => {
      checkbox.addEventListener("change", updateDeleteBtnVisibility);
    });
  }

  function updateDeleteBtnVisibility() {
    const anyChecked = document.querySelectorAll(".password-checkbox:checked").length > 0;
    deleteBtn.classList.toggle("hidden", !anyChecked);
  }

  // === Поиск ===
  function attachSearchHandler() {
    if (!searchInput || !passwordsList) return;

    searchInput.addEventListener("input", () => {
      const query = searchInput.value;
      fetch("/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ q: query }),
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.html) updatePasswordList(data.html);
        });
    });
  }

  // === Удаление выбранных ===
  function attachDeleteHandler() {
    if (!deleteBtn) return;

    deleteBtn.addEventListener("click", () => {
      const selectedIds = getSelectedIds();
      if (selectedIds.length === 0) return;

      fetch("/delete-passwords", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ids: selectedIds }),
      })
        .then((res) => {
          if (!res.ok) throw new Error("Ошибка при удалении записей");
          return res.json();
        })
        .then((data) => {
          if (data.html) {
            updatePasswordList(data.html);
          } else {
            location.reload();
          }
        })
        .catch((err) => {
          console.error("Ошибка при удалении:", err);
        });
    });
  }

  // === Вспомогательные функции ===
  function getSelectedIds() {
    return Array.from(document.querySelectorAll(".password-checkbox:checked"))
      .map((cb) => cb.dataset.id);
  }

  function updatePasswordList(html) {
    passwordsList.innerHTML = html;
    attachPasswordEntryHandlers();
    attachCheckboxHandlers();
    updateDeleteBtnVisibility();
  }

  function copyToClipboard(text, el) {
    navigator.clipboard.writeText(text).then(() => {
        const old = el.innerText;
        el.innerText = "Copied!";
        setTimeout(() => { el.innerText = old; }, 900);
    });
}
});



