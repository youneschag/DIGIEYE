const modal = document.querySelector(".modal-content");
const closeButton = document.querySelector(".close");
const confirmButton = document.getElementById("identifiant-form-confirm");

// Fonction pour afficher la fenêtre modale
function showModal() {
  modal.style.display = "block";
}

// Fonction pour masquer la fenêtre modale
function hideModal() {
  modal.style.display = "none";
}

// Événement au clic sur le bouton de fermeture
closeButton.addEventListener("click", hideModal);

// Événement au clic sur le bouton "Confirmer"
confirmButton.addEventListener("click", (e) => {
    e.preventDefault();
  // Fermer la fenêtre modale
  hideModal();
});

// Événement soumission du formulaire
const changePasswordForgotForm = document.getElementById("changePasswordForgotForm");
changePasswordForgotForm.addEventListener("submit", (e) => {
  e.preventDefault();

  // Récupérer les valeurs des champs de saisie
  const newPassword = document.getElementById("newPasswordField").value;
  const confirmNewPassword = document.getElementById("confirmNewPasswordField").value;

  // Fermer la fenêtre modale
  hideModal();
});

closeButtons.forEach((button) => {
    button.addEventListener('click', () => {
      const modal = button.closest('.modal-content');
      modal.style.display = 'none';
    });
  });
  
  window.addEventListener('click', (event) => {
    const modals = document.querySelectorAll('.modal-content');
    modals.forEach((modal) => {
      if (event.target === modal) {
        modal.style.display = 'none';
      }
    });
  });


