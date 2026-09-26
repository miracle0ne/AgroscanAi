document.addEventListener("DOMContentLoaded", () => {

    /*
     * ==============================
     * SHOW / HIDE PASSWORD
     * ==============================
     */

    const toggleButtons = document.querySelectorAll(".toggle-password");

    toggleButtons.forEach((button) => {

        button.addEventListener("click", () => {

            const targetId = button.dataset.target;
            const input = document.getElementById(targetId);

            if (!input) {
                return;
            }

            if (input.type === "password") {
                input.type = "text";
                button.textContent = "Hide";
            } else {
                input.type = "password";
                button.textContent = "Show";
            }

        });

    });


    /*
     * ==============================
     * PASSWORD STRENGTH
     * ==============================
     */

    const passwordInput = document.getElementById("password");
    const strengthBar = document.getElementById("passwordStrength");
    const strengthText = document.getElementById("passwordStrengthText");

    if (passwordInput && strengthBar && strengthText) {

        passwordInput.addEventListener("input", () => {

            const password = passwordInput.value;

            let score = 0;

            if (password.length >= 8) {
                score++;
            }

            if (/[a-z]/.test(password)) {
                score++;
            }

            if (/[A-Z]/.test(password)) {
                score++;
            }

            if (/[0-9]/.test(password)) {
                score++;
            }

            if (/[^A-Za-z0-9]/.test(password)) {
                score++;
            }


            const levels = {
                0: {
                    width: 0,
                    text: "Password strength"
                },
                1: {
                    width: 20,
                    text: "Very weak"
                },
                2: {
                    width: 40,
                    text: "Weak"
                },
                3: {
                    width: 60,
                    text: "Fair"
                },
                4: {
                    width: 80,
                    text: "Strong"
                },
                5: {
                    width: 100,
                    text: "Very strong"
                }
            };

            const level = levels[score];

            strengthBar.style.width = `${level.width}%`;
            strengthText.textContent = level.text;

        });

    }


    /*
     * ==============================
     * CONFIRM PASSWORD
     * ==============================
     */

    const confirmInput = document.getElementById("confirm_password");

    if (passwordInput && confirmInput) {

        confirmInput.addEventListener("input", () => {

            if (!confirmInput.value) {

                confirmInput.classList.remove(
                    "is-valid",
                    "is-invalid"
                );

                return;
            }

            if (passwordInput.value === confirmInput.value) {

                confirmInput.classList.remove("is-invalid");
                confirmInput.classList.add("is-valid");

            } else {

                confirmInput.classList.remove("is-valid");
                confirmInput.classList.add("is-invalid");

            }

        });

    }

});
