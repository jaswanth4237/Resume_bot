const crypto = require('crypto');
const { extractText } = require('../parsers');
const { extractResume, extractJobDescription } = require('../ai/extractors');
const { matchSkills } = require('../matching/skillMatcher');
const { calculateScores } = require('../matching/scoring');
const { evaluateEligibility } = require('../matching/eligibility');
const { recommendations } = require('./courseService');

const store = new Map();
function id() { return crypto.randomUUID(); }
function educationSatisfied(resume, requirements) { return requirements.length === 0 || requirements.some(req => resume.education.some(edu => String(edu.degree).toLowerCase().includes(String(req.degree).toLowerCase().split(' ')[0]))); }
function analyzeDocuments({ resumeFilename, resumeBytes, jdFilename, jdBytes }) {
  return Promise.all([extractText(resumeFilename, resumeBytes), extractText(jdFilename, jdBytes)]).then(([resumeText, jdText]) => {
    const resume = extractResume(resumeText), jd = extractJobDescription(jdText);
    const skills = matchSkills(resume.skills, jd.mandatory_requirements.skills, jd.preferred_requirements.skills);
    const candidateYears = Math.max(resume.total_experience_years, resume.experience.reduce((sum, item) => sum + (item.years || 0), 0));
    const requiredYears = jd.mandatory_requirements.minimum_experience_years;
    const experienceGap = Math.max(0, Number((requiredYears - candidateYears).toFixed(2)));
    const experienceScore = requiredYears ? Math.min(100, (candidateYears / requiredYears) * 100) : 100;
    const responsibilitiesScore = jd.responsibilities.length ? Math.min(100, resumeText.length > 0 ? 100 : 0) : 100;
    const educationOk = educationSatisfied(resume, jd.education_requirements);
    const scores = calculateScores(skills, experienceScore, responsibilitiesScore, educationOk ? 100 : 0);
    const eligibility = evaluateEligibility(scores.overall_score, skills.missing.filter(item => item.is_mandatory).map(item => item.skill), experienceGap, educationOk);
    const gaps = [...skills.missing.map(item => ({ skill: item.skill, gap_type: 'MISSING_SKILL', priority: item.is_mandatory ? 'CRITICAL' : 'HIGH', description: `Missing ${item.is_mandatory ? 'mandatory' : 'preferred'} skill: ${item.skill}` })), ...(experienceGap > 0 ? [{ skill: 'Years of Experience', gap_type: 'EXPERIENCE_GAP', priority: 'CRITICAL', description: `Short by ${experienceGap} years of required experience` }] : []), ...skills.partial.map(item => ({ skill: item.skill, gap_type: 'PARTIAL_SKILL', priority: 'MEDIUM', description: `Partial match for ${item.skill} (candidate has ${item.candidate_skill})` }))];
    const result = { analysis_id: id(), candidate: resume.candidate, job_title: jd.job_title, overall_score: scores.overall_score, decision: eligibility.decision, decision_reasons: eligibility.decision_reasons, category_scores: scores.category_scores, matched_requirements: skills.matched.map(item => item.skill), partial_requirements: skills.partial.map(item => item.skill), missing_requirements: skills.missing.map(item => item.skill), mandatory_failures: eligibility.mandatory_failures, experience_gap: { required_years: requiredYears, candidate_years: Number(candidateYears.toFixed(2)), gap_years: experienceGap }, gaps, explanation: gaps.length ? `Candidate has ${gaps.filter(gap => gap.priority === 'CRITICAL').length} critical requirement gaps.` : 'Candidate demonstrates solid coverage for key job requirements.', course_recommendations: recommendations(gaps) };
    store.set(result.analysis_id, result);
    return result;
  });
}
function getAnalysis(analysisId) { return store.get(analysisId); }
function setAnalysis(result) { store.set(result.analysis_id, result); }
module.exports = { analyzeDocuments, getAnalysis, setAnalysis, store };
