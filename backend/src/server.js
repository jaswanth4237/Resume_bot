const express = require('express');
const cors = require('cors');
const settings = require('./config/settings');
const api = require('./routes/api');
const { connectMongo, disconnectMongo } = require('./db/mongo');
const { DocumentProcessingError } = require('./parsers');

const app = express();
app.use(cors());
app.use(express.json());
app.get('/', (req, res) => res.json({ message: 'Welcome to ResumeMatch AI API', health_endpoint: '/api/v1/health', docs: '/docs' }));
app.use('/api/v1', api);
app.use((error, req, res, next) => { const status = error instanceof DocumentProcessingError || error.code === 'LIMIT_FILE_SIZE' ? 400 : 500; res.status(status).json({ success: false, detail: { code: error.code || 'INTERNAL_SERVER_ERROR', message: error.message } }); });

async function start() { await connectMongo(); return app.listen(settings.port, '0.0.0.0', () => console.log(`ResumeMatch API listening on port ${settings.port}`)); }
if (require.main === module) { start(); process.on('SIGTERM', async () => { await disconnectMongo(); process.exit(0); }); }
module.exports = { app, start };
