const Analysis = require('../models/analysis');
const User = require('../models/user');
const { setAnalysis } = require('./analysisService');
const { mongoStatus } = require('../db/mongo');
async function persistAnalysis(result) { if (mongoStatus() !== 'connected') return result; await Analysis.findOneAndUpdate({ analysisId: result.analysis_id }, { analysisId: result.analysis_id, result }, { upsert: true, new: true }); return result; }
async function loadAnalysis(analysisId) { if (mongoStatus() !== 'connected') return null; const record = await Analysis.findOne({ analysisId }); return record?.result || null; }
async function upsertUser(user) { if (mongoStatus() === 'connected') await User.findOneAndUpdate({ telegramId: String(user.id) }, { telegramId: String(user.id), firstName: user.first_name, username: user.username, lastSeenAt: new Date() }, { upsert: true }); }
async function persistAndCache(result) { setAnalysis(result); return persistAnalysis(result); }
module.exports = { persistAnalysis, loadAnalysis, upsertUser, persistAndCache };
