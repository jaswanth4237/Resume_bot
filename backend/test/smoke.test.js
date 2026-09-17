const test = require('node:test');
const assert = require('node:assert/strict');
const { app } = require('../src/server');
const { extractResume, extractJobDescription } = require('../src/ai/extractors');

test('server exports the API and deterministic extractors work', () => {
  assert.equal(typeof app, 'function');
  const resume = extractResume('Name: Ada Lovelace\n5 years Python, Node.js and MongoDB experience');
  const jd = extractJobDescription('Job Title: Backend Engineer\nRequired: Python, Mongo\nMinimum experience: 3 years');
  assert.equal(resume.candidate.name, 'Ada Lovelace');
  assert.ok(resume.skills.some(skill => skill.name === 'Python'));
  assert.ok(jd.mandatory_requirements.minimum_experience_years >= 3);
});
