const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
  telegramId: { 
    type: String, 
    required: true,
     unique: true,
      index: true 
    },
  firstName: String,
  username: String,
  lastSeenAt: { type: Date, default: Date.now }
}, { timestamps: true });

module.exports = mongoose.models.User || mongoose.model('User', userSchema);
