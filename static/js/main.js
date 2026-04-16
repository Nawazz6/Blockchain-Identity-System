function togglePassword(inputId, buttonElement) {
    const input = document.getElementById(inputId);
    if (!input) return;

    if (input.type === "password") {
        input.type = "text";
        buttonElement.textContent = "Hide";
    } else {
        input.type = "password";
        buttonElement.textContent = "Show";
    }
}

function validatePasswordValue(password) {
    const minLength = password.length >= 8;
    const hasUppercase = /[A-Z]/.test(password);
    const hasLowercase = /[a-z]/.test(password);
    const hasNumber = /[0-9]/.test(password);

    return minLength && hasUppercase && hasLowercase && hasNumber;
}

function generateCaptcha(type) {
    const num1 = Math.floor(Math.random() * 9) + 1;
    const num2 = Math.floor(Math.random() * 9) + 1;
    const answer = num1 + num2;

    const questionElement = document.getElementById(type + "CaptchaQuestion");
    const expectedElement = document.getElementById(type + "CaptchaExpected");
    const answerElement = document.getElementById(type + "CaptchaAnswer");

    if (questionElement) {
        questionElement.textContent = `${num1} + ${num2} = ?`;
    }

    if (expectedElement) {
        expectedElement.value = answer;
    }

    if (answerElement) {
        answerElement.value = "";
    }
}

function validateRegisterForm() {
    const passwordField = document.getElementById("registerPassword");
    const captchaAnswer = document.getElementById("registerCaptchaAnswer");
    const captchaExpected = document.getElementById("registerCaptchaExpected");

    if (!passwordField || !captchaAnswer || !captchaExpected) {
        return true;
    }

    if (!validatePasswordValue(passwordField.value)) {
        alert("Password must be at least 8 characters long and include uppercase, lowercase, and a number.");
        return false;
    }

    if (captchaAnswer.value.trim() !== captchaExpected.value.trim()) {
        alert("Captcha is incorrect.");
        generateCaptcha("register");
        return false;
    }

    return true;
}

function validateLoginForm() {
    const captchaAnswer = document.getElementById("loginCaptchaAnswer");
    const captchaExpected = document.getElementById("loginCaptchaExpected");

    if (!captchaAnswer || !captchaExpected) {
        return true;
    }

    if (captchaAnswer.value.trim() !== captchaExpected.value.trim()) {
        alert("Captcha is incorrect.");
        generateCaptcha("login");
        return false;
    }

    return true;
}

function showDashboardSection(sectionId, element) {
    const panels = document.querySelectorAll(".dashboard-section-panel");
    panels.forEach(panel => panel.classList.remove("active-panel"));

    const links = document.querySelectorAll(".sidebar-link");
    links.forEach(link => link.classList.remove("active"));

    const targetPanel = document.getElementById(sectionId);
    if (targetPanel) {
        targetPanel.classList.add("active-panel");
    }

    if (element) {
        element.classList.add("active");
    }
}