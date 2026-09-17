const crypto = require('crypto');
const { mongoStatus } = require('../db/mongo');
const { redisStatus } = require('../db/redis');
function health(req, res) { const mongo = mongoStatus(); res.json({ success: true, data: { status: mongo === 'disconnected' ? 'degraded' : 'healthy', services: { database: mongo === 'connected' ? 'connected' : mongo, redis: redisStatus() } }, requestId: crypto.randomUUID() }); }
module.exports = { health };
