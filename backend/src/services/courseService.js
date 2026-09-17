const fs = require('fs');
const path = require('path');
const { normalizeSkill } = require('../ai/extractors');
const catalogPath = path.join(__dirname, '../../data/courses.json');
let catalog;
function getCatalog() { if (!catalog) catalog = JSON.parse(fs.readFileSync(catalogPath, 'utf8')); return catalog; }
function recommendations(gaps) {
  const skills = gaps.filter(gap => ['MISSING_SKILL', 'PARTIAL_SKILL'].includes(gap.gap_type)).map(gap => normalizeSkill(gap.skill).toLowerCase());
  const seen = new Set();
  return getCatalog().filter(course => skills.some(skill => skill.includes(normalizeSkill(course.skill).toLowerCase()) || normalizeSkill(course.skill).toLowerCase().includes(skill))).filter(course => { if (seen.has(course.title)) return false; seen.add(course.title); return true; }).slice(0, 5).map(course => ({ ...course, gap_skill: normalizeSkill(course.skill) }));
}
module.exports = { getCatalog, recommendations };
