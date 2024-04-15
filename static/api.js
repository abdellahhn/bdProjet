let user = JSON.parse(sessionStorage.getItem('user')) || [];

function updateUserSession(userData) {
    sessionStorage.setItem('user', JSON.stringify(userData));
}

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

    signupForm.addEventListener('submit', function (event) {
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
                user.push(formData.get('email'));
                updateUserSession(user);
                loginNotice.textContent = "Connexion réussie!";
                // window.location.href = '/';
                console.log(user)
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


async function addProduitAuPanier(nom, prix, quantite) {
    console.log(nom, prix, quantite);
    debugger;
    if (user.length === 0) {
        window.location.href = "http://127.0.0.1:5000";
    } else {
        console.log(nom, prix, quantite);
        let prix_total = quantite * prix

        try {
            const res = await fetch("/addProductToCart", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    email: user[0],
                    nom: nom,
                    quantite: quantite,
                    prix: prix_total,
                })
            });


            if (!res.ok) {
                throw new Error("Échec de l'ajout de l'article. Vérifiez la réponse du serveur.");
            }

            return await res.json();
        } catch (error) {
            console.error("Error:", error);
            throw error;
        }
    }
}


async function addArticleToDatabase() {
    debugger;
    if (user.length === 0) {
            window.location.href= "http://127.0.0.1:5000";

    } else {

        // Get the form element by its ID
        const form = document.getElementById('ajtArticle'); // Replace with your actual form ID
        console.log(form)

        // Use FormData to access form data
        const formData = new FormData(form);
        console.log(formData)

        // Extract individual field values
        const nomArticle = formData.get('title');
        const prix = Number(formData.get('price'));
        const quantite = Number(formData.get('quantity'));
        const marque = formData.get('brand');

        console.log(nomArticle, prix, quantite, marque);

        try {
            const res = await fetch("/addArticle", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    nom: nomArticle,
                    quantite: quantite,
                    prix: prix,
                    marque: marque
                })
            });

            console.log(nomArticle)

            if (!res.ok) {
                throw new Error("Échec de l'ajout de l'article. Vérifiez la réponse du serveur.");
            }

            return await res.json();
        } catch (error) {
            console.error("Error:", error);
            throw error;
        }
    }
}

async function logout() {
    debugger
    updateUserSession('')
    user.length = 0;
    window.location.href = "http://127.0.0.1:5000";
}


async function acheterCommandesAPI(event) {
    event.preventDefault();

    debugger;
    if (user.length === 0) {
        window.location.href = "http://127.0.0.1:5000";
    } else {
        const form = document.getElementById('acheterPanier');

        const formData = new FormData(form);

    const cardType = document.getElementById('card_type').value;
    const cardNumber = Number(document.getElementById('card_number').value);
    const securityCode = Number(document.getElementById('security_code').value);
    const expirationDate = document.getElementById('expiration_date').value;

        try {
            const res = await fetch("/commandes", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    email: user[0],
                    type: cardType,
                    numero: cardNumber,
                    code: securityCode,
                    date: expirationDate,
                })
            });


            if (!res.ok) {
                throw new Error("Échec de l'ajout de l'article. Vérifiez la réponse du serveur.");
            }
            return await res.json();
        } catch (error) {
            console.error("Error:", error);
            throw error;
        }
    }
}

async function viderPanier() {
    try {
        const response = await fetch("/viderPanier", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ email: user[0] })
        });

        if (!response.ok) {
            throw new Error("Erreur lors de la suppression du panier.");
        }

        const data = await response.json();
        console.log(data.message); // Afficher le message de la réponse

        // Traitez la réponse comme nécessaire ici
    } catch (error) {
        console.error("Erreur:", error);
        // Gérez les erreurs comme nécessaire
    }
}



