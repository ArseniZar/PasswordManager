export function copyToClipboard(text, el) {
  navigator.clipboard.writeText(text).then(() => {
    const original = el.innerText;
    el.innerText = "Copied!";
    setTimeout(() => {
      el.innerText = original;
    }, 900);
  }).catch(err => {
    console.error("[clipboard] Failed to copy:", err);
  });
}
