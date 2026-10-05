// Asks before destructive actions and shows progress while Gemini is working.
document.addEventListener("submit", (event) => {
  const form = event.target;
  if (form.dataset.confirm && !window.confirm(form.dataset.confirm)) {
    event.preventDefault();
    return;
  }
  const button = form.querySelector("button[type=submit]");
  if (button && form.dataset.busy) {
    button.disabled = true;
    button.textContent = form.dataset.busy;
  }
});

// Coming back with the browser's Back button should not leave a disabled button.
window.addEventListener("pageshow", (event) => {
  if (event.persisted) window.location.reload();
});
