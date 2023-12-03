const nodemon = require('nodemon');

nodemon({
  script: 'client.js',
  ext: 'js json', // Monitor changes to .js and .json files
});

nodemon.on('start', () => {
  console.log('Client server has started');
});

nodemon.on('restart', (files) => {
  console.log('Client server restarting due to changes in:', files);
});