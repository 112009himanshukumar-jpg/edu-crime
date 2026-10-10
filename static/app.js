document.addEventListener("DOMContentLoaded", () => {
  // Highlight selected answers with a clear keyboard-accessible state.
  document.querySelectorAll(".answer-option input").forEach((input) => {
    input.addEventListener("change", () => {
      document.querySelectorAll(".answer-option").forEach((label) => label.classList.remove("selected"));
      const label = input.closest(".answer-option");
      if (label) label.classList.add("selected");
    });
  });

  const form = document.getElementById("answer-form");
  if (form) {
    form.addEventListener("submit", (event) => {
      const selected = form.querySelector('input[name="answer"]:checked');
      if (!selected) {
        event.preventDefault();
        alert("Choose an answer before continuing.");
      }
    });
  }
});
