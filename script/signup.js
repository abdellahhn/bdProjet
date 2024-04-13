export default function handleSignupForm() {
  const signupForm = document.getElementById('signup-form');
  const signupNotice = document.getElementById('signup-notice');

  signupForm.addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent default form submission

    const formData = new FormData(this);
    const userData = {};
    formData.forEach((value, key) => {
      userData[key] = value;
    });

    fetch('/signup', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(userData)
    })
    .then(response => response.json())
    .then(data => {
      signupNotice.textContent = data.message; // Update notice text
      signupNotice.classList.add(data.type); // Add CSS class for styling
      // Optionally: Clear the form after successful signup
      if (data.type === 'success') {
        signupForm.reset();
      }
    })
    .catch(error => {
      console.error('Error:', error);
      signupNotice.textContent = "Une erreur est survenue lors de la création du compte.";
      signupNotice.classList.add('error');
    });
  });
}
