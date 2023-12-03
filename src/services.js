// Define the services variable in the global scope
let services = [];

// Export the services array so that it can be imported in other files
export { services };

const { ipcRenderer } = require('electron');

function sendPasswordToServer(password) {
  ipcRenderer.send('sendPasswordToServer', password);
}