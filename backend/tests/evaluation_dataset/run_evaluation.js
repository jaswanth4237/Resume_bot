/**
 * Evaluation runner — measures scoring & decision accuracy against labeled cases.
 * Run: node tests/evaluation_dataset/run_evaluation.js
 */
const fs = require('fs');
const path = require('path');
const { extractResume, extractJobDescription } = require('../../src/ai/extractors');
const { matchSkills } = require('../../src/matching/skillMatcher');
const { calculateScores } = require('../../src/matching/scoring');
const { evaluateEligibility } = require('../../src/matching/eligibility');

const DATASET_DIR = __dirname;

function loadCases() {
    return fs.readdirSync(DATASET_DIR)
        .filter(name => name.startsWith('case_') && fs.statSync(path.join(DATASET_DIR, name)).isDirectory())
        .map(name => {
            const dir = path.join(DATASET_DIR, name);
            return {
                id: name,
                resumeText: fs.readFileSync(path.join(dir, 'resume.txt'), 'utf8'),
                jdText: fs.readFileSync(path.join(dir, 'jd.txt'), 'utf8'),
                expected: JSON.parse(fs.readFileSync(path.join(dir, 'expected.json'), 'utf8'))
            };
        });
}

function runCase({ id, resumeText, jdText, expected }) {
    const resume = extractResume(resumeText);
    const jd = extractJobDescription(jdText);
    const skills = matchSkills(resume.skills, jd.mandatory_requirements.skills, jd.preferred_requirements.skills);
    const candidateYears = Math.max(resume.total_experience_years, resume.experience.reduce((s, e) => s + (e.years || 0), 0));
    const requiredYears = jd.mandatory_requirements.minimum_experience_years;
    const expGap = Math.max(0, requiredYears - candidateYears);
    const expScore = requiredYears ? Math.min(100, (candidateYears / requiredYears) * 100) : 100;
    const scores = calculateScores(skills, expScore, 100, resume.education.length > 0 ? 100 : (jd.education_requirements.some(r => r.is_mandatory) ? 0 : 100));
    const missingMandatory = skills.missing.filter(m => m.is_mandatory).map(m => m.skill);
    const eligibility = evaluateEligibility(scores.overall_score, missingMandatory, expGap, true);

    const decisionMatch = eligibility.decision === expected.expected_decision;
    const [minScore, maxScore] = expected.expected_score_range;
    const scoreInRange = scores.overall_score >= minScore && scores.overall_score <= maxScore;

    return { id, expected: expected.expected_decision, actual: eligibility.decision, score: scores.overall_score, decisionMatch, scoreInRange, missingMandatory };
}

function main() {
    const cases = loadCases();
    if (!cases.length) { console.error('No evaluation cases found.'); process.exit(1); }

    console.log('\n══════════════════════════════════════════════════════');
    console.log('  RESUMEMATCH AI — EVALUATION RESULTS');
    console.log('══════════════════════════════════════════════════════\n');

    let correct = 0, total = cases.length;
    const results = cases.map(c => {
        const r = runCase(c);
        if (r.decisionMatch) correct++;
        const status = r.decisionMatch ? '✅ PASS' : '❌ FAIL';
        console.log(`${status}  ${r.id.padEnd(12)} | Expected: ${r.expected.padEnd(12)} | Actual: ${r.actual.padEnd(12)} | Score: ${r.score.toFixed(1)}%`);
        if (!r.decisionMatch) {
            console.log(`         Missing mandatory: [${r.missingMandatory.join(', ')}]`);
        }
        return r;
    });

    const accuracy = ((correct / total) * 100).toFixed(1);
    console.log('\n──────────────────────────────────────────────────────');
    console.log(`  Decision Accuracy: ${correct}/${total} (${accuracy}%)`);
    console.log('══════════════════════════════════════════════════════\n');

    if (correct < total) process.exitCode = 1;
}

main();
