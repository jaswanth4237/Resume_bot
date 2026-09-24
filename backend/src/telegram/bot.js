const { Bot, InlineKeyboard, Keyboard } = require('grammy');
const fs = require('fs');
const path = require('path');
const settings = require('../config/settings');
const { extractText } = require('../parsers');
const { analyzeDocuments } = require('../services/analysisService');
const { persistAndCache, upsertUser } = require('../services/persistenceService');

const sessions = new Map();
const sessionFile = path.join(__dirname, '../../data/telegram_sessions.json');

function saveSessions() {
  const stored = Object.fromEntries([...sessions.entries()].map(([id, value]) => [id, {
    jd: value.jd ? { filename: value.jd.filename, bytes: value.jd.bytes.toString('base64') } : null,
    resumes: value.resumes.map(item => ({ filename: item.filename, bytes: item.bytes.toString('base64') }))
  }]));
  fs.writeFileSync(sessionFile, JSON.stringify(stored));
}

function loadSession(id) {
  try {
    const stored = JSON.parse(fs.readFileSync(sessionFile, 'utf8'))[id];
    if (!stored) return null;
    return {
      jd: stored.jd ? { filename: stored.jd.filename, bytes: Buffer.from(stored.jd.bytes, 'base64') } : null,
      resumes: (stored.resumes || []).map(item => ({ filename: item.filename, bytes: Buffer.from(item.bytes, 'base64') }))
    };
  } catch (error) {
    return null;
  }
}

function session(id) {
  if (!sessions.has(id)) sessions.set(id, loadSession(id) || { jd: null, resumes: [] });
  return sessions.get(id);
}

function reset(id) {
  sessions.set(id, { jd: null, resumes: [] });
  saveSessions();
  return session(id);
}

function keyboard() {
  return new Keyboard().text('Start Analysis').text('/status').text('/reset').resized();
}

function analyzeKeyboard() {
  return new InlineKeyboard().text('Start Analysis', 'start_analysis').text('Analyze', 'analyze');
}

function documentType(filename, caption, text = '') {
  const metadata = `${caption} ${filename}`.toLowerCase().replace(/[_-]+/g, ' ');
  if (/\b(resume|cv|curriculum vitae)\b/.test(metadata)) return 'resume';
  if (/\b(jd|job description|job posting|vacancy)\b/.test(metadata)) return 'jd';

  const content = text.toLowerCase();
  const resumeSignals = (content.match(/\b(resume|curriculum vitae|work experience|employment history|education|certifications?|objective|skills)\b/g) || []).length;
  const jdSignals = (content.match(/\b(job description|responsibilities|qualifications?|requirements?|must have|required|preferred|we are looking|position|role)\b/g) || []).length;
  if (resumeSignals > jdSignals && resumeSignals > 0) return 'resume';
  if (jdSignals > 0) return 'jd';
  return 'unknown';
}

function welcome(ctx) {
  reset(ctx.from.id);
  return ctx.reply('Welcome to ResumeMatch AI. Please upload the Job Description first, then upload one Resume.', { reply_markup: keyboard() });
}

async function downloadTelegramFile(filePath) {
  const response = await fetch(`https://api.telegram.org/file/bot${settings.telegramBotToken}/${filePath}`);
  if (!response.ok) {
    throw new Error(`Telegram file download failed with status ${response.status}.`);
  }
  return Buffer.from(await response.arrayBuffer());
}

function learningLinks(result) {
  const recommendations = result.course_recommendations || [];
  const linkedSkills = new Set(recommendations.map(item => item.gap_skill));
  const gaps = (result.gaps || [])
    .filter(gap => ['MISSING_SKILL', 'PARTIAL_SKILL'].includes(gap.gap_type))
    .map(gap => gap.skill)
    .filter((skill, index, skills) => skills.indexOf(skill) === index);

  if (!gaps.length) return '\n\nSKILL GAPS\nNone identified.';

  const lines = gaps.map(skill => {
    const query = encodeURIComponent(`learn ${skill} skills tutorial`);
    return `- ${skill}:\n  Google learning results: https://www.google.com/search?q=${query}\n  YouTube tutorials: https://www.youtube.com/results?search_query=${query}`;
  });
  return `\n\nSKILL GAPS AND LEARNING LINKS\n${lines.join('\n')}`;
}

async function replyLong(ctx, text) {
  const chunks = [];
  let remaining = text;
  while (remaining.length > 3900) {
    let splitAt = remaining.lastIndexOf('\n', 3900);
    if (splitAt < 1) splitAt = 3900;
    chunks.push(remaining.slice(0, splitAt));
    remaining = remaining.slice(splitAt).trimStart();
  }
  if (remaining) chunks.push(remaining);
  for (const chunk of chunks) await ctx.reply(chunk);
}

async function analyzeSession(ctx) {
  const current = session(ctx.from.id);
  if (!current.jd || !current.resumes.length) {
    return ctx.reply('Upload a Job Description and at least one resume first.');
  }
  if (current.analyzing) return ctx.reply('Analysis is already in progress. Please wait for the result.');
  current.analyzing = true;

  try {
    const results = await Promise.all(current.resumes.map(item => analyzeDocuments({
      resumeFilename: item.filename,
      resumeBytes: item.bytes,
      jdFilename: current.jd.filename,
      jdBytes: current.jd.bytes
    }).then(persistAndCache)));

    for (const result of results) {
      await replyLong(ctx, `RESUME MATCH REPORT\n\nCandidate: ${result.candidate.name}\nPosition: ${result.job_title}\nScore: ${result.overall_score}%\nDecision: ${result.decision}\n\n${result.explanation}${learningLinks(result)}`);
    }
    current.jd = null;
    current.resumes = [];
    saveSessions();
  } catch (error) {
    console.error('Telegram analysis failed:', error);
    await ctx.reply('Analysis could not be completed. Please try again or use /reset to upload the files again.');
  } finally {
    current.analyzing = false;
  }
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
      return ctx.reply('Only the first Resume is considered. This file was not added. Tap Analyze to continue or use /reset to start over.', { reply_markup: analyzeKeyboard() });
    }
    const caption = (ctx.message.caption || '').toLowerCase();
    const metadataType = documentType(filename, caption);

    if (!current.jd && metadataType === 'resume') {
      return ctx.reply('This looks like a Resume. Please upload the Job Description first.');
    }
    if (current.jd && metadataType === 'jd') {
      return ctx.reply('A Job Description is already uploaded. Please send the first Resume.');
    }

    try {
      const file = await ctx.getFile();
      const bytes = await downloadTelegramFile(file.file_path);
      const type = documentType(filename, caption, await extractText(filename, bytes));

      if (!current.jd && type !== 'jd') {
        return ctx.reply('Please upload the Job Description first. This file was not considered as a Job Description.');
      }

      if (!current.jd) {
        current.jd = { filename, bytes };
        saveSessions();
        return ctx.reply(`Job Description received: ${filename}. Now send the Resume.`, { reply_markup: keyboard() });
      }

      if (type === 'jd') {
        return ctx.reply('A Job Description is already uploaded. Please send the first Resume.');
      }

      current.resumes.push({ filename, bytes });
      saveSessions();
      return ctx.reply(`Resume received: ${filename}. The first Resume will be used. Tap Start Analysis to begin.`, { reply_markup: analyzeKeyboard() });
    } catch (error) {
      console.error('Telegram document processing failed:', error);
      return ctx.reply('I could not download or read that file. Please try uploading it again.');
    }
  });

  bot.hears(/^(analyze|start analysis)$/i, analyzeSession);

  bot.callbackQuery(/^(analyze|start_analysis)$/, async ctx => {
    await ctx.answerCallbackQuery();
    return analyzeSession(ctx);
  });

  bot.on('message:text', ctx => ctx.reply('Send a Job Description or Resume file, then tap Analyze.', {
    reply_markup: new InlineKeyboard().text('Analyze')
  }));

  bot.catch(error => {
    console.error('Telegram update failed:', error.error);
  });

  return bot;
}

module.exports = { createBot, sessions, documentType, learningLinks, replyLong };
