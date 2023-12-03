const identifiantForm = document.getElementById("identifiant-form");
const identifiantButton = document.getElementById("identifiant-form-submit");

let failedAttempts = 0; // Compteur de tentatives infructueuses

identifiantButton.addEventListener("click", (e) => {
  e.preventDefault();
  const username = identifiantForm.username.value;
  localStorage.setItem("loggedInUsername", username);

  // Vérifier si l'identifiant est connu
  if (username === "younes") {
    window.location.href = "create_account.html";
  } else {
    failedAttempts++;
    if (failedAttempts === 3) {
      window.location.href = "create_account.html";
    } else {
      alert("Cet identifiant est inexistant. Tentative " + failedAttempts + "/3");
    }
  }
});
