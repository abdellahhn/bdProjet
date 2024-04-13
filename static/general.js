let user = []

function isListeUtilisateursVide() {
  return user.length === 0;
}

function ajouterUtilisateur(email) {
  user.push(email);
  console.log(user)
}


export { isListeUtilisateursVide, ajouterUtilisateur };
