let user = {email:""}


const validateEmail = (email) => {
  return String(email)
    .toLowerCase()
    .match(
      /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|.(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
    );
};

async function signup() {
  const signupForm = document.getElementById('signup-form');
  const signupNotice = document.getElementById('signup-notice');

  signupForm.addEventListener('submit', function(event) {
    event.preventDefault();

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
      signupNotice.textContent = data.message;
      signupNotice.classList.add(data.type);

      if (data.type === 'success') {
        window.location.href = "http://127.0.0.1:5000/home"
        signupNotice.style.display = 'block';
      } else {
        signupNotice.style.display = 'block';
      }
    })
    .catch(error => {
      console.error('Error:', error);
      signupNotice.textContent = "Une erreur est survenue lors de la création du compte.";
      signupNotice.classList.add('error');
      signupNotice.style.display = 'block';
    });
  });
}

async function logIn() {
    let email = document.getElementById("email").value
    let password = document.getElementById("motdepasse").value
    const loginForm = document.getElementById('login-form');
    const loginNotice = document.getElementById('login-notice');

    loginForm.addEventListener('submit', async (event) => {
      event.preventDefault();

      const formData = new FormData(loginForm);
      const userData = {};
      formData.forEach((value, key) => {
        userData[key] = value;
      });

      try {
        const response = await fetch('/login', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(userData)
        });

        if (!response.ok) {
          throw new Error(`Error: ${response.status}`);
        }

        const loginData = await response.json();
        loginNotice.textContent = loginData.message;

        if (loginData.status === 200) {
          localStorage.setItem("email", `${email}`)
          loginNotice.textContent = "Connexion réussie!";
          window.location.href = '/';
        } else {
          loginNotice.textContent = "Email ou mot de passe incorrect.";
        }

        loginNotice.style.display = 'block';
      } catch (error) {
        console.error('Error:', error);
        loginNotice.textContent = 'Une erreur est survenue lors de la connexion.';
        loginNotice.classList.add('error');
        loginNotice.style.display = 'block';
      }
    });
}

async function addProduitAuPanier() {
    debugger;
    if (localStorage.getItem('email') === "") {
        window.location.href = "http://127.0.0.1:5000";
    } else {
        const selectionMenu = document.getElementById('quantite');
        const quantite = parseInt(selectionMenu.value);  // Get the quantity selected by the user

        try {
            const res = await fetch("http://127.0.0.1:5000/panier", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    email: localStorage.getItem("email"),
                    quantite: quantite,
                })
            });

            const response = await res.json();
            const div = document.getElementById('message');
            const infosDajout = document.createElement('div');
            infosDajout.innerText = "Produit ajouté";
            div.appendChild(infosDajout);

        } catch (error) {
            console.error("Error:", error);
            const div = document.getElementById('message');
            const infosDajout = document.createElement('div');
            infosDajout.innerText = "Une erreur est survenue";
            div.appendChild(infosDajout);
        }
    }
}


// export { isListeUtilisateursVide, ajouterUtilisateur, logIn, signup };
window.user = user;
