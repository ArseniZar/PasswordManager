import { attachPasswordEntryHandlers } from "./handlers/passwordEntry.js";
import { attachCheckboxHandlers, updateDeleteBtnVisibility } from "./handlers/checkbox.js";
import { attachSearchHandler } from "./handlers/search.js";
import { attachDeleteHandler } from "./handlers/delete.js";
import { attachAlertHandlers } from "./handlers/alert.js"; 

document.addEventListener("DOMContentLoaded", () => {
  function init() {
    attachPasswordEntryHandlers();
    attachCheckboxHandlers();
    attachSearchHandler();
    attachDeleteHandler();
    updateDeleteBtnVisibility();
    attachAlertHandlers();
  }

  init();
});
