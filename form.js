document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById('leadForm');
  const submitButton = form.querySelector('button');

  form.addEventListener('submit', async function (e) {
    e.preventDefault();

    const data = {
      name: document.getElementById('name').value,
      email: document.getElementById('email').value,
      phone: document.getElementById('phone').value,
      city: document.getElementById('city').value,
      state: document.getElementById('state').value
    };

    submitButton.disabled = true;
    submitButton.textContent = "Submitting...";

    try {
      const response = await fetch('RENDER LINK HERE/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const result = await response.json();

      const oldMessage = document.getElementById('successMessage');
      if (oldMessage) oldMessage.remove();

      const message = document.createElement("div");
      message.id = "successMessage";
      message.textContent = "✅ Success! A professional from our service network will be reaching out soon.";
      message.style.backgroundColor = "#d4edda";
      message.style.color = "#155724";
      message.style.padding = "15px";
      message.style.border = "1px solid #c3e6cb";
      message.style.borderRadius = "5px";
      message.style.marginTop = "20px";
      message.style.textAlign = "center";
      message.style.fontWeight = "bold";

      document.querySelector(".form-container").appendChild(message);
      form.reset();
    } catch (error) {
      alert("Something went wrong. Please try again in a moment.");
      console.error("Submission error:", error);
    } finally {
      submitButton.disabled = false;
      submitButton.textContent = "Get Started";
    }
  });
});
