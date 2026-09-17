const { Bot, InlineKeyboard, Keyboard } = require('grammy');
const settings = require('../config/settings');
const { analyzeDocuments } = require('../services/analysisService');
const { persistAndCache, upsertUser } = require('../services/persistenceService');

const sessions = new Map();

function session(id) {
  if (!sessions.has(id)) sessions.set(id, { jd: null, resumes: [] });
  return sessions.get(id);
}

function reset(id) {
  sessions.set(id, { jd: null, resumes: [] });
  return session(id);
}

function keyboard() {
  return new Keyboard().text('Start Analysis').text('/status').text('/reset').resized();
}

function analyzeKeyboard() {
  return new Keyboard().text('Analyze').text('/status').text('/reset').resized();
}

function welcome(ctx) {
  reset(ctx.from.id);
  return ctx.reply('Welcome to ResumeMatch AI. Send a Job Description or Resume to begin.', { reply_markup: keyboard() });
}

async function downloadTelegramFile(filePath) {
  const response = await fetch(`https://api.telegram.org/file/bot${settings.telegramBotToken}/${filePath}`);
  if (!response.ok) {
    throw new Error(`Telegram file download failed with status ${response.status}.`);
  }
  return Buffer.from(await response.arrayBuffer());
}

async function createBot() {
  if (!settings.telegramBotToken) return null;

  const bot = new Bot(settings.telegramBotToken);

  bot.command('start', async ctx => {
    await upsertUser(ctx.from);
    return welcome(ctx);
  });

  bot.hears(/^(hi|hello)$/i, welcome);

  bot.command('reset', ctx => {
    reset(ctx.from.id);
    return ctx.reply('Session cleared.', { reply_markup: keyboard() });
  });

  bot.command('status', ctx => {
    const current = session(ctx.from.id);
    return ctx.reply(`Job Description: ${current.jd ? current.jd.filename : 'Not uploaded'}\nResumes: ${current.resumes.length}`);
  });

  bot.on('message:document', async ctx => {
    const document = ctx.message.document;
    const filename = document.file_name || 'document.txt';
    if (!/\.(pdf|docx|txt)$/i.test(filename)) {
      return ctx.reply('Unsupported format. Please upload PDF, DOCX, or TXT.');
    }

    const current = session(ctx.from.id);
    if (current.jd && current.resumes.length) {
      return ctx.reply('Both files are already uploaded. Tap Analyze or use /reset to start over.', { reply_markup: analyzeKeyboard() });
    }
    const caption = (ctx.message.caption || '').toLowerCase();
    const isJd = /\b(jd|job|description)\b/i.test(`${caption} ${filename}`);
    const isResume = /\b(resume|cv)\b/i.test(`${caption} ${filename}`);

    if (current.jd && isJd) {
      return ctx.reply('A Job Description is already uploaded. Please send a Resume.');
    }
    if (current.resumes.length && isResume) {
      return ctx.reply('A Resume is already uploaded. Please send the Job Description.');
    }

    const file = await ctx.getFile();
    const bytes = await downloadTelegramFile(file.file_path);
    const shouldStoreAsJd = current.resumes.length > 0 || (!current.jd && !isResume);

    if (shouldStoreAsJd && !current.jd) {
      current.jd = { filename, bytes };
      return ctx.reply(`Job Description received: ${filename}. Now send the Resume.`, { reply_markup: keyboard() });
    }

    current.resumes.push({ filename, bytes });
    if (!current.jd) {
      return ctx.reply(`Resume received: ${filename}. Now send the Job Description.`, { reply_markup: keyboard() });
    }
    return ctx.reply(`Resume #${current.resumes.length} received: ${filename}. Both files are ready.`, { reply_markup: analyzeKeyboard() });
  });

  bot.hears(/^(analyze|start analysis)$/i, async ctx => {
    const current = session(ctx.from.id);
    if (!current.jd || !current.resumes.length) {
      return ctx.reply('Upload a Job Description and at least one resume first.');
    }

    const results = await Promise.all(current.resumes.map(item => analyzeDocuments({
      resumeFilename: item.filename,
      resumeBytes: item.bytes,
      jdFilename: current.jd.filename,
      jdBytes: current.jd.bytes
    }).then(persistAndCache)));

    current.resumes = [];
    for (const result of results) {
      await ctx.reply(`RESUME MATCH REPORT\n\nCandidate: ${result.candidate.name}\nPosition: ${result.job_title}\nScore: ${result.overall_score}%\nDecision: ${result.decision}\n\n${result.explanation}`);
    }
  });

  bot.on('message:text', ctx => ctx.reply('Send a Job Description or Resume file, then tap Analyze.', {
    reply_markup: new InlineKeyboard().text('Analyze')
  }));

  bot.catch(error => {
    console.error('Telegram update failed:', error.error);
  });

  return bot;
}

module.exports = { createBot, sessions };
