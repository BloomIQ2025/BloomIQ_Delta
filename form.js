document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById('leadForm');
  const submitButton = form.querySelector('button');

  // Set hidden page_url field for visibility (even though we include it in payload)
  const pageUrl = window.location.href.split('#')[0];
  const pageUrlInput = document.getElementById('page_url');
  if (pageUrlInput) pageUrlInput.value = pageUrl;

  form.addEventListener('submit', async function (e) {
    e.preventDefault();

    const consentCheckbox = document.getElementById('privacyConsent');
    if (!consentCheckbox.checked) {
      alert("Please confirm that you have read and agree to the Privacy Policy.");
      return;
    }

    const data = {
      name: document.getElementById('name').value.trim(),
      email: document.getElementById('email').value.trim(),
      phone: document.getElementById('phone').value.trim(),
      city: document.getElementById('city').value.trim(),
      state: document.getElementById('state').value.trim(),
      privacy_ack: consentCheckbox.checked ? 'true' : 'false',
      page_url: pageUrl
    };

    submitButton.disabled = true;
    submitButton.textContent = "Submitting...";

    try {
      const response = await fetch('https://bloomiq-delta.onrender.com/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      });

      // Log status for troubleshooting
      console.log('Submit response status:', response.status);

      if (!response.ok) {
        const errTxt = await response.text();
        console.error('Server error body:', errTxt);
        alert("Submission failed. Please try again in a moment.");
        return;
      }

      const result = await response.json();
      console.log('Submit response JSON:', result);

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
      console.error("Network or CORS error:", error);
      alert("Something went wrong. Please try again in a moment.");
    } finally {
      submitButton.disabled = false;
      submitButton.textContent = "Get Started";
    }
  });
});