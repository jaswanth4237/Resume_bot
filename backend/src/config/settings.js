require('dotenv').config();

module.exports = {
  appEnv: process.env.APP_ENV || 'development',
  port: Number(process.env.PORT || 8000),
  mongodbUri: process.env.MONGODB_URI || '',
  redisUrl: process.env.REDIS_URL || '',
  telegramBotToken: process.env.TELEGRAM_BOT_TOKEN || '',
  llmApiKey: process.env.LLM_API_KEY || '',
  maxFileSizeMb: Number(process.env.MAX_FILE_SIZE_MB || 10),
  suitableThreshold: Number(process.env.SUITABLE_THRESHOLD || 75),
  borderlineThreshold: Number(process.env.BORDERLINE_THRESHOLD || 60),
  analysisRateLimitSeconds: Number(process.env.ANALYSIS_RATE_LIMIT_SECONDS || 10)
};
