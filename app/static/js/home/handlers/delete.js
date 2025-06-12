import { updatePasswordList } from "../utils/dom.js";

export function attachDeleteHandler() {
  const deleteBtn = document.getElementById("delete-selected-btn");
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
        if (!res.ok) throw new Error("Delete request failed");
        return res.json();
      })
      .then((data) => {
        if (data.html) {
          updatePasswordList(data.html);
          location.reload();
        } else {
          location.reload();
        }
      })
      .catch((err) => console.error("[delete] Error:", err));
  });
}

function getSelectedIds() {
  return Array.from(
    document.querySelectorAll(".password-checkbox:checked")
  ).map((cb) => cb.dataset.id);
}
