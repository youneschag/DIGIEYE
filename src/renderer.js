const { ipcRenderer } = require('electron');

  ipcRenderer.on('services', (event, services) => {
    const servicesList = document.getElementById('services');
    services.sort((a, b) => a.name.localeCompare(b.name)); // Tri des services en ordre alphabétique
    services.forEach((service) => {
      const listItem = document.createElement('li');
      listItem.textContent = service.name;
      listItem.onclick = () => ipcRenderer.send('displayRubrique', { serviceName: service.name });
      servicesList.appendChild(listItem);
    });
  });

  ipcRenderer.send('getServices');

  ipcRenderer.on('displayRubrique', (event, { serviceName }) => {
    ipcRenderer.send('getRubrique', serviceName);
  });

  ipcRenderer.on('rubrique', (event, rubrique) => {
    window.alert(rubrique);
  });

  // Function for refresh by clicking the banner
function refreshWindow() {
  window.location.reload();
}

function sendClicked() {
  showPasswordConfirmationModal();
}
