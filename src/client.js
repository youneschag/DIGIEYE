const dgram = require('dgram');
const fs = require('fs');
const net = require('net');
const ip = require('ip');

const client = dgram.createSocket('udp4');

// Obtenez l'adresse IP locale
const clientIpAddress = ip.address();

client.send(JSON.stringify({ clientIp: clientIpAddress }), 3784, '224.0.0.2', (err) => {
  if (err) {
    console.error('Error sending client IP:', err);
  } else {
    console.log('Sent client IP:', clientIpAddress);
    setupUnicastServer();
  }
});

function setupUnicastServer() {
  const server = net.createServer((socket) => {
    socket.on('data', (data) => {
      const services = JSON.parse(data);
      console.log('Received services from server:', services);
      fs.writeFileSync('server_services.json', JSON.stringify(services));
    });
  });

  server.listen(3784, () => {
    console.log('Server listening for unicast connections on port 3784');
  });

  server.on('error', (err) => {
    console.error('Server error:', err);
  });
}

// Lecture des services à partir du fichier client_services.json
fs.readFile('client_services.json', 'utf8', (err, clientServicesData) => {
  if (err) {
    console.error('Error reading client_services.json:', err);
    return;
  }

  // Parsing des données depuis client_services.json
  const clientServices = JSON.parse(clientServicesData);

  setTimeout(() => {
    const message = Buffer.from(JSON.stringify(clientServices));
    client.send(message, 0, message.length, 3785, '224.0.0.2', (err) => {
      if (err) {
        console.error('Error sending multicast:', err);
      } else {
        console.log('Sent multicast services:', clientServices);
        fs.writeFileSync('server_services.json', JSON.stringify(clientServices));
      }
      client.close();
    });
  }, 2000);  
});





