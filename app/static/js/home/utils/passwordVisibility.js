export function togglePasswordVisibility() {
    document.querySelectorAll(".toggle-password-btn").forEach(function (btn) {
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        const targetId = btn.dataset.target;
        const pwd = document.getElementById(targetId);
        if (pwd) {
          if (pwd.type === "password") {
            pwd.type = "text";
            btn.textContent = "🔒";
          } else {
            pwd.type = "password";
            btn.textContent = "👁";
          }
        }
      });
    });
  }

  document.addEventListener("DOMContentLoaded", togglePasswordVisibility);