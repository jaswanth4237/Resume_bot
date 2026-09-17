const { normalizeSkill } = require('../ai/extractors');
const strictPairs = require('../../data/skill_aliases.json').strict_inequivalent || [];

function equivalent(a, b) {
  const left = normalizeSkill(a).toLowerCase();
  const right = normalizeSkill(b).toLowerCase();
  if (left === right || left.includes(right) || right.includes(left)) return true;
  if (strictPairs.some(pair => pair.map(item => normalizeSkill(item).toLowerCase()).includes(left) && pair.map(item => normalizeSkill(item).toLowerCase()).includes(right))) return false;
  return left.split(/[^a-z0-9]+/).some(token => token.length > 2 && right.includes(token));
}

function matchSkills(candidateSkills, mandatorySkills, preferredSkills) {
  const matched = [], partial = [], missing = [];
  const requirements = [...mandatorySkills.map(skill => [skill, true]), ...preferredSkills.filter(skill => !mandatorySkills.includes(skill)).map(skill => [skill, false])];
  for (const [skill, isMandatory] of requirements) {
    const exact = candidateSkills.find(candidate => normalizeSkill(candidate.name).toLowerCase() === normalizeSkill(skill).toLowerCase());
    if (exact) { matched.push({ skill, normalized_skill: normalizeSkill(skill), evidence: exact.evidence, match_type: 'EXACT', confidence: 1, is_mandatory: isMandatory }); continue; }
    const related = candidateSkills.find(candidate => equivalent(skill, candidate.name));
    if (related) partial.push({ skill, normalized_skill: normalizeSkill(skill), candidate_skill: related.name, evidence: related.evidence, match_type: 'PARTIAL', confidence: 0.85, is_mandatory: isMandatory });
    else missing.push({ skill, normalized_skill: normalizeSkill(skill), evidence: 'No evidence found in candidate resume', match_type: 'MISSING', confidence: 0, is_mandatory: isMandatory });
  }
  const score = (items, total) => total ? ((items.matched + items.partial * 0.5) / total) * 100 : 100;
  return { matched, partial, missing, mandatory_score: Math.min(100, Number(score({ matched: matched.filter(item => item.is_mandatory).length, partial: partial.filter(item => item.is_mandatory).length }, mandatorySkills.length).toFixed(2))), preferred_score: Math.min(100, Number(score({ matched: matched.filter(item => !item.is_mandatory).length, partial: partial.filter(item => !item.is_mandatory).length }, preferredSkills.length).toFixed(2))) };
}

module.exports = { matchSkills };
