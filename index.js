const sdk = require('api')('https://localhost:8000/');

sdk.auth('<auth_code>');
sdk.sockettoken()
  .then(({ data }) => console.log(data))
  .catch(err => console.error(err));