const mongoose = require('mongoose');

const analysisSchema = new mongoose.Schema({
    analysisId: { type: String, required: true, unique: true, index: true },
    result: { type: mongoose.Schema.Types.Mixed, required: true }
}, { timestamps: true });

module.exports = mongoose.models.Analysis || mongoose.model('Analysis', analysisSchema);
