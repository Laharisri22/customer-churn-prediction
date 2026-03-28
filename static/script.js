function toggleMode() {
    const body = document.body;
    const btn = document.querySelector(".toggle-container button");

    // If going to LIGHT mode → add animation
    if (!body.classList.contains("light-mode")) {
        body.classList.add("light-transition");  // enable smooth
        body.classList.add("light-mode");

        btn.innerHTML = "☀️";

        // remove transition after animation (so dark mode is instant)
        setTimeout(() => {
            body.classList.remove("light-transition");
        }, 600);

    } else {
        // Back to DARK (no animation)
        body.classList.remove("light-mode");
        btn.innerHTML = "🌙";
    }
}