export function attachCheckboxHandlers() {
  document.querySelectorAll(".password-checkbox").forEach(checkbox => {
    checkbox.addEventListener("change", updateDeleteBtnVisibility);
  });
}

export function updateDeleteBtnVisibility() {
  const deleteBtn = document.getElementById("delete-selected-btn");
  const checkedCount = document.querySelectorAll(".password-checkbox:checked").length;
  deleteBtn?.classList.toggle("hidden", checkedCount === 0);
}