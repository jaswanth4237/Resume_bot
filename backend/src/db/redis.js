const settings = require('../config/settings');

function redisStatus() {
  return settings.redisUrl ? 'configured' : 'disabled';
}

module.exports = { redisStatus };
