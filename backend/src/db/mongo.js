const mongoose = require('mongoose');
const settings = require('../config/settings');

let state = 'disabled';

async function connectMongo() {
  if (!settings.mongodbUri) {
    state = 'disabled';
    return false;
  }
  try {
    await mongoose.connect(settings.mongodbUri, {
      dbName: 'resumematch',
      family: 4,
      serverSelectionTimeoutMS: 10000
    });
    state = 'connected';
    return true;
  } catch (error) {
    state = 'disconnected';
    console.warn(`MongoDB is unavailable: ${error.message}`);
    return false;
  }
}

async function disconnectMongo() {
  if (mongoose.connection.readyState !== 0) await mongoose.disconnect();
  state = settings.mongodbUri ? 'disconnected' : 'disabled';
}

function mongoStatus() {
  return state;
}

module.exports = { connectMongo, disconnectMongo, mongoStatus };
