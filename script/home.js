// Script pour gérer la transformation des boutons login/signup en profil/déconnexion

const loginBtn = document.querySelector('.login');
const signupBtn = document.querySelector('.signup');

const profileBtn = document.querySelector('.profile');
const logoutBtn = document.querySelector('.logout');
const searchbtn = document.querySelector('.recherche')

// Fonction pour afficher les boutons profil/déconnexion
function showLoggedInButtons() {
  loginBtn.classList.add('hidden');
  signupBtn.classList.add('hidden');
  profileBtn.classList.remove('hidden');
  logoutBtn.classList.remove('hidden');
}

// Fonction pour afficher les boutons login/signup
function showLoggedOutButtons() {
  loginBtn.classList.remove('hidden');
  signupBtn.classList.remove('hidden');
  profileBtn.classList.add('hidden');
  logoutBtn.classList.add('hidden'); // This line was already there

  // Additional logic to handle user logged out state (optional)
  // You can add code here to clear any user data or perform other actions
  // when the user logs out. For example:
  console.log("Utilisateur déconnecté");
}

// Call the appropriate function based on user login status (implementation needed)
// This part is not included in the provided code as it depends on your specific authentication system.
// You'll need to replace this comment with code that checks if the user is logged in
// and calls the appropriate function (showLoggedInButtons or showLoggedOutButtons).

// Example (replace with your actual logic):
if (isUserLoggedIn()) {
  showLoggedInButtons();
} else {
  showLoggedOutButtons();
}
