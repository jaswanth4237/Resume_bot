const skillAliases = require('../../data/skill_aliases.json');

const aliasMap = Object.fromEntries(Object.entries(skillAliases.aliases || {}).map(([key, value]) => [key.toLowerCase(), value]));
const knownSkills = [...new Set(Object.values(aliasMap).concat(Object.keys(aliasMap)))];

function normalizeSkill(skill) {
  const value = String(skill || '').trim().replace(/\s+/g, ' ');
  return aliasMap[value.toLowerCase()] || value;
}

function unique(values) {
  return [...new Set(values.filter(Boolean).map(normalizeSkill))];
}

function findSkills(text) {
  const lower = text.toLowerCase();
  const names = unique(knownSkills.filter(skill => lower.includes(skill.toLowerCase())));
  return names.map(name => ({ name, level: 'intermediate', years: 0, evidence: `Found in document as ${name}` }));
}

function extractYears(text) {
  const matches = [...text.matchAll(/(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)/gi)].map(match => Number(match[1]));
  return matches.length ? Math.max(...matches) : 0;
}

function extractName(text, fallback = 'Candidate') {
  const labeled = text.match(/name\s*[:\-]\s*([A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,3})/i);
  if (labeled) return labeled[1].trim();
  const firstLine = text.split(/\r?\n/).map(line => line.trim()).find(line => /^[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+){1,3}$/.test(line));
  return firstLine || fallback;
}

function extractResume(text) {
  const skills = findSkills(text);
  return {
    candidate: { name: extractName(text), email: (text.match(/[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}/) || [null])[0], phone: (text.match(/[+\d][\d ()-]{7,}/) || [null])[0] },
    skills,
    experience: [{ company: 'Document evidence', role: 'Professional experience', years: extractYears(text), description: text.slice(0, 500), technologies: skills.map(skill => skill.name) }],
    education: /bachelor|master|phd|degree|university|college/i.test(text) ? [{ institution: 'Document evidence', degree: (text.match(/(bachelor[^,.;\n]*|master[^,.;\n]*|phd)/i) || ['Bachelor'])[0] }] : [],
    projects: [],
    certifications: [],
    total_experience_years: extractYears(text)
  };
}

function extractList(text, pattern) {
  const section = text.match(pattern);
  if (!section) return [];
  return section[1].split(/[,;\n|]/).map(item => item.replace(/^[-*•]\s*/, '').trim()).filter(item => item.length > 1 && item.length < 80);
}

function extractJobDescription(text) {
  const skills = findSkills(text).map(item => item.name);
  const mandatory = extractList(text, /(?:required|mandatory|must have|minimum qualifications?)\s*[:\-]?([\s\S]{0,500})/i);
  const preferred = extractList(text, /(?:preferred|nice to have|good to have)\s*[:\-]?([\s\S]{0,400})/i);
  const requiredYears = extractYears(text);
  const mandatorySkills = unique(mandatory.concat(skills.filter(skill => new RegExp(`(?:required|must|mandatory)[^\\n]{0,80}${skill}`, 'i').test(text))));
  const preferredSkills = unique(preferred.concat(skills.filter(skill => !mandatorySkills.map(normalizeSkill).includes(normalizeSkill(skill)))));
  return {
    job_title: (text.match(/(?:job title|position|role)\s*[:\-]\s*([^\n]+)/i) || [])[1]?.trim() || 'Software Engineer',
    mandatory_requirements: { skills: mandatorySkills, minimum_experience_years: requiredYears },
    preferred_requirements: { skills: preferredSkills },
    education_requirements: /bachelor|master|degree|university|college/i.test(text) ? [{ degree: 'Bachelor', field: 'Computer Science', is_mandatory: /required|must|mandatory/i.test(text) }] : [],
    responsibilities: extractList(text, /(?:responsibilities|what you will do|duties)\s*[:\-]?([\s\S]{0,700})/i)
  };
}

module.exports = { normalizeSkill, extractResume, extractJobDescription };
