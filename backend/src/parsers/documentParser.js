const path = require('path');
const pdfParse = require('pdf-parse');
const mammoth = require('mammoth');

class DocumentProcessingError extends Error {
  constructor(code, message) {
    super(message);
    this.code = code;
  }
}

async function extractText(filename, buffer) {
  const ext = path.extname(filename || '').toLowerCase();
  if (!Buffer.isBuffer(buffer)) throw new DocumentProcessingError('INVALID_FILE', 'File content is required.');
  try {
    if (ext === '.txt') return buffer.toString('utf8').trim();
    if (ext === '.pdf') return (await pdfParse(buffer)).text.trim();
    if (ext === '.docx') return (await mammoth.extractRawText({ buffer })).value.trim();
  } catch (error) {
    throw new DocumentProcessingError('PARSE_ERROR', `Unable to parse ${filename}: ${error.message}`);
  }
  throw new DocumentProcessingError('UNSUPPORTED_FORMAT', 'Supported formats are PDF, DOCX, and TXT.');
}

module.exports = { extractText, DocumentProcessingError };
