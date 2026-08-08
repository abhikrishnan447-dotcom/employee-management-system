function togglePassword(inputId, iconId) {
    const input = document.getElementById(inputId);
    const icon = document.getElementById(iconId);
    if (!input || !icon) return;
    if (input.type === "password") {
        input.type = "text";
        icon.classList.remove("bi-eye");
        icon.classList.add("bi-eye-slash");
    } else {
        input.type = "password";
        icon.classList.remove("bi-eye-slash");
        icon.classList.add("bi-eye");
    }
}

document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("registerForm");
    const phone = document.getElementById("phone");
    const photoInput = document.getElementById("profile_photo");

    if (phone) phone.addEventListener("input", function () { this.value = this.value.replace(/\D/g, "").slice(0, 10); });

    if (photoInput) photoInput.addEventListener("change", function () {
        const file = this.files[0];
        if (!file) return;
        if (!["image/jpeg", "image/png"].includes(file.type)) { alert("Please select a JPG or PNG image."); this.value = ""; return; }
        if (file.size > 2 * 1024 * 1024) { alert("Profile photo must be smaller than 2 MB."); this.value = ""; return; }
        const reader = new FileReader();
        reader.onload = function (event) {
            const preview = document.getElementById("photoPreview");
            const placeholder = document.getElementById("photoPlaceholder");
            if (preview) { preview.src = event.target.result; preview.style.display = "block"; }
            if (placeholder) placeholder.style.display = "none";
        };
        reader.readAsDataURL(file);
    });

    const emailField = document.getElementById("email");
    if (emailField && !document.getElementById("department")) {
        const emailColumn = emailField.closest(".col-md-6");
        const departmentColumn = document.createElement("div");
        departmentColumn.className = "col-md-6";
        departmentColumn.innerHTML = '<label class="form-label" for="department">Department</label><div class="input-wrap"><i class="bi bi-building"></i><select id="department" name="department" class="form-control" required><option value="">Select Department</option></select></div><div class="validation-message" id="departmentError">Please select a department.</div>';
        if (emailColumn && emailColumn.parentNode) emailColumn.parentNode.insertBefore(departmentColumn, emailColumn);

        fetch("/register/departments/")
            .then(response => response.json())
            .then(data => {
                const select = document.getElementById("department");
                if (!select) return;
                data.departments.forEach(department => {
                    const option = document.createElement("option");
                    option.value = department.id;
                    option.textContent = department.name;
                    select.appendChild(option);
                });
            })
            .catch(() => {
                const select = document.getElementById("department");
                if (select) {
                    const option = document.createElement("option");
                    option.textContent = "Unable to load departments";
                    option.disabled = true;
                    select.appendChild(option);
                }
            });
    }

    if (!form) return;
    form.addEventListener("submit", function (event) {
        let valid = true;
        const name = document.getElementById("name");
        const nameError = document.getElementById("nameError");
        if (!/^[A-Za-z ]{3,}$/.test(name.value.trim())) { name.classList.add("is-invalid"); if (nameError) nameError.style.display = "block"; valid = false; }
        else { name.classList.remove("is-invalid"); if (nameError) nameError.style.display = "none"; }

        const phoneValue = phone ? phone.value.trim() : "";
        const phoneError = document.getElementById("phoneError");
        if (!/^[0-9]{10}$/.test(phoneValue)) { if (phone) phone.classList.add("is-invalid"); if (phoneError) phoneError.style.display = "block"; valid = false; }
        else { if (phone) phone.classList.remove("is-invalid"); if (phoneError) phoneError.style.display = "none"; }

        const department = document.getElementById("department");
        const departmentError = document.getElementById("departmentError");
        if (!department || !department.value) { if (department) department.classList.add("is-invalid"); if (departmentError) departmentError.style.display = "block"; valid = false; }
        else { department.classList.remove("is-invalid"); if (departmentError) departmentError.style.display = "none"; }

        const email = document.getElementById("email");
        const emailError = document.getElementById("emailError");
        if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value.trim())) { email.classList.add("is-invalid"); if (emailError) emailError.style.display = "block"; valid = false; }
        else { email.classList.remove("is-invalid"); if (emailError) emailError.style.display = "none"; }

        const password = document.getElementById("password");
        const passwordError = document.getElementById("passwordError");
        if (!/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/.test(password.value)) { password.classList.add("is-invalid"); if (passwordError) passwordError.style.display = "block"; valid = false; }
        else { password.classList.remove("is-invalid"); if (passwordError) passwordError.style.display = "none"; }

        const confirmPassword = document.getElementById("confirm_password");
        const confirmError = document.getElementById("confirmError");
        if (confirmPassword.value !== password.value || confirmPassword.value === "") { confirmPassword.classList.add("is-invalid"); if (confirmError) confirmError.style.display = "block"; valid = false; }
        else { confirmPassword.classList.remove("is-invalid"); if (confirmError) confirmError.style.display = "none"; }

        if (!valid) event.preventDefault();
    });
});
