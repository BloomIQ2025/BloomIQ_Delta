document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById('leadForm');
  const submitButton = form.querySelector('button');

  form.addEventListener('submit', async function (e) {
    e.preventDefault();

    const consentCheckbox = document.getElementById('privacyConsent');
    if (!consentCheckbox.checked) {
      alert("Please confirm that you have read and agree to the Privacy Policy.");
      return;
    }

    // ✅ Collect form data + timestamp + current page URL
    const data = {
      name: document.getElementById('name').value,
      email: document.getElementById('email').value,
      phone: document.getElementById('phone').value,
      city: document.getElementById('city').value,
      state: document.getElementById('state').value,
      timestamp: new Date().toISOString(), // ⏰ Add timestamp
      page_url: window.location.href        // 🌐 Add current page URL
    };

    submitButton.disabled = true;
    submitButton.textContent = "Submitting...";

    try {
      const response = await fetch('https://bloomiq-delta.onrender.com/submit', {
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

      // ✅ Remove old message if it exists
      const oldMessage = document.getElementById('successMessage');
      if (oldMessage) oldMessage.remove();

      // ✅ Show success message
      const message = document.createElement("div");
      message.id = "successMessage";
      message.textContent = "✅ Success!";
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
