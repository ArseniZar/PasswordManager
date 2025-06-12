import { updatePasswordList } from "../utils/dom.js";

export function attachSearchHandler() {
  const searchInput = document.getElementById("search");
  if (!searchInput) return;

  searchInput.addEventListener("input", () => {
    const query = searchInput.value.trim();

    fetch("/search", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ q: query }),
    })
      .then(res => {
        if (!res.ok) throw new Error("Search request failed");
        return res.json();
      })
      .then(data => updatePasswordList(data.html))
      .catch(err => console.error("[search] Error:", err));
  });
}
