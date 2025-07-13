document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("leadForm");

    form.addEventListener("submit", function (event) {
        event.preventDefault();

        const formData = {
            name: document.getElementById("name").value,
            email: document.getElementById("email").value,
            phone: document.getElementById("phone").value,
            city: document.getElementById("city").value,
            state: document.getElementById("state").value
        };

        fetch("/submit", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(formData)
        })
        .then(response => {
            if (response.ok) {
                alert("Thank you! Your information has been submitted.");
                form.reset();
            } else {
                alert("There was an error submitting your form. Please try again.");
            }
        })
        .catch(error => {
            console.error("Error:", error);
            alert("There was a problem submitting your form.");
        });
    });
});
