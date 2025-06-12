import { attachPasswordEntryHandlers } from "../handlers/passwordEntry.js";
import { attachCheckboxHandlers, updateDeleteBtnVisibility } from "../handlers/checkbox.js";


export function updatePasswordList(html) {
  
  const passwordsList = document.getElementById("passwords-list");
  if (!passwordsList) return;
  document.querySelectorAll('.password-checkbox').forEach(checkbox => {
  checkbox.checked = false;
  });

  passwordsList.innerHTML = html;
  attachPasswordEntryHandlers();
  attachCheckboxHandlers();
  updateDeleteBtnVisibility();

 
}

