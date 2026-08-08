
function togglePassword(inputId, iconId) {

    const input =
        document.getElementById(inputId);

    const icon =
        document.getElementById(iconId);


    if (input.type === "password") {

        input.type = "text";

        icon.classList.remove("bi-eye");

        icon.classList.add("bi-eye-slash");

    }

    else {

        input.type = "password";

        icon.classList.remove("bi-eye-slash");

        icon.classList.add("bi-eye");

    }

}




const phone =
    document.getElementById("phone");


phone.addEventListener("input", function () {

    this.value =
        this.value.replace(/\D/g, "");

    if (this.value.length > 10) {

        this.value =
            this.value.slice(0, 10);

    }

});





const photoInput =
    document.getElementById("profile_photo");


photoInput.addEventListener(
    "change",
    function () {

        const file =
            this.files[0];

        if (!file) {
            return;
        }


        const allowedTypes = [
            "image/jpeg",
            "image/png"
        ];


        if (!allowedTypes.includes(file.type)) {

            alert(
                "Please select a JPG or PNG image."
            );

            this.value = "";

            return;
        }


        if (file.size > 2 * 1024 * 1024) {

            alert(
                "Profile photo must be smaller than 2 MB."
            );

            this.value = "";

            return;
        }


        const reader =
            new FileReader();


        reader.onload =
            function (event) {

                const preview =
                    document.getElementById(
                        "photoPreview"
                    );

                const placeholder =
                    document.getElementById(
                        "photoPlaceholder"
                    );


                preview.src =
                    event.target.result;

                preview.style.display =
                    "block";

                placeholder.style.display =
                    "none";

            };


        reader.readAsDataURL(file);

    }
);





document
    .getElementById("registerForm")
    .addEventListener(
        "submit",
        function (event) {


            let valid = true;


            /* NAME */

            const name =
                document.getElementById("name");

            const nameError =
                document.getElementById("nameError");


            const namePattern =
                /^[A-Za-z ]{3,}$/;


            if (!namePattern.test(name.value.trim())) {

                name.classList.add("is-invalid");

                nameError.style.display =
                    "block";

                valid = false;

            }

            else {

                name.classList.remove("is-invalid");

                nameError.style.display =
                    "none";

            }



            /* PHONE */

            const phoneValue =
                phone.value.trim();

            const phoneError =
                document.getElementById("phoneError");


            if (!/^[0-9]{10}$/.test(phoneValue)) {

                phone.classList.add("is-invalid");

                phoneError.style.display =
                    "block";

                valid = false;

            }

            else {

                phone.classList.remove("is-invalid");

                phoneError.style.display =
                    "none";

            }



            /* DEPARTMENT */

            const department =
                document.getElementById("department");

            const departmentError =
                document.getElementById(
                    "departmentError"
                );


            if (!department.value) {

                department.classList.add(
                    "is-invalid"
                );

                departmentError.style.display =
                    "block";

                valid = false;

            }

            else {

                department.classList.remove(
                    "is-invalid"
                );

                departmentError.style.display =
                    "none";

            }



            /* EMAIL */

            const email =
                document.getElementById("email");

            const emailError =
                document.getElementById(
                    "emailError"
                );


            const emailPattern =
                /^[^\s@]+@[^\s@]+\.[^\s@]+$/;


            if (!emailPattern.test(
                email.value.trim()
            )) {

                email.classList.add(
                    "is-invalid"
                );

                emailError.style.display =
                    "block";

                valid = false;

            }

            else {

                email.classList.remove(
                    "is-invalid"
                );

                emailError.style.display =
                    "none";

            }



            /* PASSWORD */

            const password =
                document.getElementById(
                    "password"
                );


            const passwordError =
                document.getElementById(
                    "passwordError"
                );


            const passwordPattern =
                /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/;


            if (!passwordPattern.test(
                password.value
            )) {

                password.classList.add(
                    "is-invalid"
                );

                passwordError.style.display =
                    "block";

                valid = false;

            }

            else {

                password.classList.remove(
                    "is-invalid"
                );

                passwordError.style.display =
                    "none";

            }



            /* CONFIRM PASSWORD */

            const confirmPassword =
                document.getElementById(
                    "confirm_password"
                );


            const confirmError =
                document.getElementById(
                    "confirmError"
                );


            if (
                confirmPassword.value !==
                password.value ||
                confirmPassword.value === ""
            ) {

                confirmPassword.classList.add(
                    "is-invalid"
                );

                confirmError.style.display =
                    "block";

                valid = false;

            }

            else {

                confirmPassword.classList.remove(
                    "is-invalid"
                );

                confirmError.style.display =
                    "none";

            }



            /* STOP SUBMISSION */

            if (!valid) {

                event.preventDefault();

            }

        }
    );