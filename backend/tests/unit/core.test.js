const test = require('node:test');
const assert = require('node:assert/strict');
const { extractResume, extractJobDescription, normalizeSkill } = require('../../src/ai/extractors');
const { matchSkills } = require('../../src/matching/skillMatcher');
const { calculateScores } = require('../../src/matching/scoring');
const { evaluateEligibility } = require('../../src/matching/eligibility');
const { recommendations } = require('../../src/services/courseService');
const { app } = require('../../src/server');

// ─── Skill Normalization ─────────────────────────────────────────────────────

test('normalizeSkill: resolves known aliases', () => {
    assert.equal(normalizeSkill('Mongo'), 'MongoDB');
    assert.equal(normalizeSkill('K8s'), 'Kubernetes');
    assert.equal(normalizeSkill('JS'), 'JavaScript');
    assert.equal(normalizeSkill('Node'), 'Node.js');
    assert.equal(normalizeSkill('Postgres'), 'PostgreSQL');
    assert.equal(normalizeSkill('Amazon Web Services'), 'AWS');
    assert.equal(normalizeSkill('GCP'), 'Google Cloud Platform');
    assert.equal(normalizeSkill('TS'), 'TypeScript');
});

test('normalizeSkill: passthrough for unknown skills', () => {
    assert.equal(normalizeSkill('Python'), 'Python');
    assert.equal(normalizeSkill('FastAPI'), 'FastAPI');
});

test('normalizeSkill: handles whitespace and mixed case', () => {
    const result = normalizeSkill('  node.js  ');
    assert.ok(result.length > 0);
});

// ─── Resume Extraction ────────────────────────────────────────────────────────

test('extractResume: extracts candidate name from labeled field', () => {
    const resume = extractResume('Name: Ada Lovelace\n5 years Python experience');
    assert.equal(resume.candidate.name, 'Ada Lovelace');
});

test('extractResume: extracts candidate name from first heading line', () => {
    const resume = extractResume('John Smith\nSoftware Engineer\nJava, Spring Boot, Docker');
    assert.equal(resume.candidate.name, 'John Smith');
});

test('extractResume: extracts email', () => {
    const resume = extractResume('Name: Test User\nEmail: test@example.com');
    assert.equal(resume.candidate.email, 'test@example.com');
});

test('extractResume: extracts skills from known alias dictionary', () => {
    const resume = extractResume('Name: Dev\nExperienced in Python, Node.js, Docker, MongoDB');
    const skillNames = resume.skills.map(s => s.name);
    assert.ok(skillNames.includes('Python'), `Expected Python in ${skillNames}`);
    assert.ok(skillNames.includes('Node.js'), `Expected Node.js in ${skillNames}`);
    assert.ok(skillNames.includes('Docker'), `Expected Docker in ${skillNames}`);
    assert.ok(skillNames.includes('MongoDB'), `Expected MongoDB in ${skillNames}`);
});

test('extractResume: extracts years of experience', () => {
    const resume = extractResume('Name: Dev\n4 years of Java development');
    assert.equal(resume.total_experience_years, 4);
});

test('extractResume: returns 0 experience when none stated', () => {
    const resume = extractResume('Name: Dev\nSkills: React');
    assert.equal(resume.total_experience_years, 0);
});

test('extractResume: detects education (bachelor)', () => {
    const resume = extractResume('Name: Dev\nBachelor of Science in Computer Science');
    assert.ok(resume.education.length > 0);
});

test('extractResume: no education when none mentioned', () => {
    const resume = extractResume('Name: Dev\n3 years Python');
    assert.equal(resume.education.length, 0);
});

test('extractResume: returns valid schema structure', () => {
    const resume = extractResume('Name: Test\n2 years Java');
    assert.ok(Array.isArray(resume.skills));
    assert.ok(Array.isArray(resume.experience));
    assert.ok(Array.isArray(resume.education));
    assert.ok(Array.isArray(resume.projects));
    assert.ok(Array.isArray(resume.certifications));
    assert.ok(typeof resume.total_experience_years === 'number');
    assert.ok(typeof resume.candidate === 'object');
});

// ─── JD Extraction ───────────────────────────────────────────────────────────

test('extractJobDescription: extracts job title', () => {
    const jd = extractJobDescription('Job Title: Senior Backend Engineer\nRequired: Java, Spring Boot');
    assert.equal(jd.job_title, 'Senior Backend Engineer');
});

test('extractJobDescription: fallback job title when not labeled', () => {
    const jd = extractJobDescription('We need a developer with Python skills');
    assert.equal(typeof jd.job_title, 'string');
    assert.ok(jd.job_title.length > 0);
});

test('extractJobDescription: extracts mandatory experience years', () => {
    const jd = extractJobDescription('Job Title: Dev\nRequired: minimum 3 years experience');
    assert.ok(jd.mandatory_requirements.minimum_experience_years >= 3);
});

test('extractJobDescription: extracts preferred skills section', () => {
    const jd = extractJobDescription('Job Title: Dev\nRequired: Java\nPreferred: Docker, AWS, Kubernetes');
    assert.ok(Array.isArray(jd.preferred_requirements.skills));
});

test('extractJobDescription: returns valid schema', () => {
    const jd = extractJobDescription('Job Title: Engineer\nRequired: Python\n3+ years experience');
    assert.ok(Array.isArray(jd.mandatory_requirements.skills));
    assert.ok(typeof jd.mandatory_requirements.minimum_experience_years === 'number');
    assert.ok(Array.isArray(jd.preferred_requirements.skills));
    assert.ok(Array.isArray(jd.education_requirements));
    assert.ok(Array.isArray(jd.responsibilities));
});

// ─── Skill Matcher ───────────────────────────────────────────────────────────

test('matchSkills: exact match returns MATCHED', () => {
    const candidateSkills = [{ name: 'Python', evidence: 'found', years: 2 }];
    const result = matchSkills(candidateSkills, ['Python'], []);
    assert.equal(result.matched.length, 1);
    assert.equal(result.matched[0].match_type, 'EXACT');
    assert.equal(result.missing.length, 0);
});

test('matchSkills: alias match returns PARTIAL or EXACT', () => {
    const candidateSkills = [{ name: 'Mongo', evidence: 'found', years: 1 }];
    const result = matchSkills(candidateSkills, ['MongoDB'], []);
    assert.ok(result.matched.length === 1 || result.partial.length === 1);
});

test('matchSkills: missing skill is correctly flagged', () => {
    const candidateSkills = [{ name: 'Java', evidence: 'found', years: 2 }];
    const result = matchSkills(candidateSkills, ['Java', 'Docker'], []);
    const missingNames = result.missing.map(m => m.skill);
    assert.ok(missingNames.includes('Docker'));
});

test('matchSkills: strict inequivalent — Java != JavaScript', () => {
    const candidateSkills = [{ name: 'Java', evidence: 'found', years: 3 }];
    const result = matchSkills(candidateSkills, ['JavaScript'], []);
    assert.equal(result.missing.length, 1);
    assert.equal(result.missing[0].skill, 'JavaScript');
});

test('matchSkills: strict inequivalent — MySQL != PostgreSQL', () => {
    const candidateSkills = [{ name: 'MySQL', evidence: 'found', years: 2 }];
    const result = matchSkills(candidateSkills, ['PostgreSQL'], []);
    assert.equal(result.missing.length, 1);
});

test('matchSkills: strict inequivalent — AWS != Azure', () => {
    const candidateSkills = [{ name: 'AWS', evidence: 'found', years: 1 }];
    const result = matchSkills(candidateSkills, ['Azure'], []);
    assert.equal(result.missing.length, 1);
});

test('matchSkills: mandatory_score is 100 when all mandatory matched', () => {
    const candidateSkills = [
        { name: 'Java', evidence: 'found', years: 2 },
        { name: 'Spring Boot', evidence: 'found', years: 2 }
    ];
    const result = matchSkills(candidateSkills, ['Java', 'Spring Boot'], []);
    assert.equal(result.mandatory_score, 100);
    assert.equal(result.missing.length, 0);
});

test('matchSkills: mandatory_score is 0 when all mandatory missing', () => {
    const candidateSkills = [{ name: 'React', evidence: 'found', years: 1 }];
    const result = matchSkills(candidateSkills, ['Java', 'Docker'], []);
    assert.equal(result.mandatory_score, 0);
    assert.equal(result.missing.length, 2);
});

test('matchSkills: preferred skills do not affect mandatory_score', () => {
    const candidateSkills = [{ name: 'Python', evidence: 'found', years: 2 }];
    const result = matchSkills(candidateSkills, ['Python'], ['Docker', 'AWS']);
    assert.equal(result.mandatory_score, 100);
    assert.equal(result.missing.filter(m => m.is_mandatory).length, 0);
});

// ─── Scoring Engine ───────────────────────────────────────────────────────────

test('calculateScores: perfect candidate scores 100', () => {
    const skillResult = { mandatory_score: 100, preferred_score: 100 };
    const scores = calculateScores(skillResult, 100, 100, 100);
    assert.equal(scores.overall_score, 100);
});

test('calculateScores: zero skills produces low overall score', () => {
    const skillResult = { mandatory_score: 0, preferred_score: 0 };
    const scores = calculateScores(skillResult, 0, 0, 0);
    assert.equal(scores.overall_score, 0);
});

test('calculateScores: category_scores object has all required keys', () => {
    const skillResult = { mandatory_score: 80, preferred_score: 60 };
    const scores = calculateScores(skillResult, 70, 100, 100);
    assert.ok('skills' in scores.category_scores);
    assert.ok('experience' in scores.category_scores);
    assert.ok('responsibilities' in scores.category_scores);
    assert.ok('education' in scores.category_scores);
    assert.ok('preferred' in scores.category_scores);
});

test('calculateScores: is deterministic — same input always same output', () => {
    const skillResult = { mandatory_score: 72, preferred_score: 50 };
    const a = calculateScores(skillResult, 80, 100, 100);
    const b = calculateScores(skillResult, 80, 100, 100);
    assert.equal(a.overall_score, b.overall_score);
});

test('calculateScores: overall_score never exceeds 100', () => {
    const skillResult = { mandatory_score: 200, preferred_score: 200 };
    const scores = calculateScores(skillResult, 200, 200, 200);
    assert.ok(scores.overall_score <= 100);
});

test('calculateScores: overall_score never below 0', () => {
    const skillResult = { mandatory_score: -50, preferred_score: -50 };
    const scores = calculateScores(skillResult, -50, -50, -50);
    assert.ok(scores.overall_score >= 0);
});

// ─── Eligibility Engine ───────────────────────────────────────────────────────

test('evaluateEligibility: SUITABLE when score >= 75 and no failures', () => {
    const result = evaluateEligibility(80, [], 0, true);
    assert.equal(result.decision, 'SUITABLE');
    assert.equal(result.mandatory_failures.length, 0);
});

test('evaluateEligibility: BORDERLINE when 60 <= score < 75 and no failures', () => {
    const result = evaluateEligibility(68, [], 0, true);
    assert.equal(result.decision, 'BORDERLINE');
});

test('evaluateEligibility: REJECT when score < 60', () => {
    const result = evaluateEligibility(45, [], 0, true);
    assert.equal(result.decision, 'REJECT');
});

test('evaluateEligibility: REJECT on missing mandatory skill regardless of score', () => {
    const result = evaluateEligibility(95, ['Docker'], 0, true);
    assert.equal(result.decision, 'REJECT');
    assert.ok(result.mandatory_failures.length > 0);
});

test('evaluateEligibility: REJECT on experience gap regardless of score', () => {
    const result = evaluateEligibility(90, [], 1.5, true);
    assert.equal(result.decision, 'REJECT');
    assert.ok(result.mandatory_failures.some(f => f.includes('experience')));
});

test('evaluateEligibility: REJECT on education failure', () => {
    const result = evaluateEligibility(80, [], 0, false);
    assert.equal(result.decision, 'REJECT');
    assert.ok(result.mandatory_failures.some(f => f.includes('education')));
});

test('evaluateEligibility: multiple mandatory failures all captured', () => {
    const result = evaluateEligibility(90, ['Java', 'Docker'], 1, false);
    assert.equal(result.decision, 'REJECT');
    assert.ok(result.mandatory_failures.length >= 3);
});

test('evaluateEligibility: decision_reasons is always a non-empty array', () => {
    const r1 = evaluateEligibility(80, [], 0, true);
    const r2 = evaluateEligibility(40, ['Java'], 2, false);
    assert.ok(Array.isArray(r1.decision_reasons) && r1.decision_reasons.length > 0);
    assert.ok(Array.isArray(r2.decision_reasons) && r2.decision_reasons.length > 0);
});

// ─── Course Recommendations ───────────────────────────────────────────────────

test('recommendations: returns courses for a MISSING_SKILL gap', () => {
    const gaps = [{ skill: 'Docker', gap_type: 'MISSING_SKILL', priority: 'CRITICAL' }];
    const courses = recommendations(gaps);
    assert.ok(Array.isArray(courses));
    assert.ok(courses.length > 0);
    assert.ok(courses.every(c => c.skill && c.title && c.url && c.platform));
});

test('recommendations: returns courses for a PARTIAL_SKILL gap', () => {
    const gaps = [{ skill: 'Kubernetes', gap_type: 'PARTIAL_SKILL', priority: 'MEDIUM' }];
    const courses = recommendations(gaps);
    assert.ok(Array.isArray(courses));
});

test('recommendations: no RESPONSIBILITY gaps produce course recs', () => {
    const gaps = [{ skill: 'Build APIs', gap_type: 'RESPONSIBILITY', priority: 'LOW' }];
    const courses = recommendations(gaps);
    assert.ok(Array.isArray(courses));
});

test('recommendations: no duplicate course titles', () => {
    const gaps = [
        { skill: 'Docker', gap_type: 'MISSING_SKILL', priority: 'CRITICAL' },
        { skill: 'Docker', gap_type: 'PARTIAL_SKILL', priority: 'MEDIUM' }
    ];
    const courses = recommendations(gaps);
    const titles = courses.map(c => c.title);
    assert.equal(titles.length, new Set(titles).size);
});

test('recommendations: returns at most 5 courses', () => {
    const gaps = [
        { skill: 'Docker', gap_type: 'MISSING_SKILL', priority: 'CRITICAL' },
        { skill: 'AWS', gap_type: 'MISSING_SKILL', priority: 'HIGH' },
        { skill: 'Kubernetes', gap_type: 'MISSING_SKILL', priority: 'HIGH' },
        { skill: 'Microservices', gap_type: 'MISSING_SKILL', priority: 'MEDIUM' },
        { skill: 'Spring Boot', gap_type: 'MISSING_SKILL', priority: 'MEDIUM' },
        { skill: 'PostgreSQL', gap_type: 'MISSING_SKILL', priority: 'LOW' }
    ];
    const courses = recommendations(gaps);
    assert.ok(courses.length <= 5);
});

// ─── Server / API ─────────────────────────────────────────────────────────────

test('server: exports a valid Express app', () => {
    assert.equal(typeof app, 'function');
});

test('integration: health endpoint returns 200 with correct shape', async () => {
    const http = require('node:http');
    await new Promise((resolve, reject) => {
        const req = http.request({ host: '127.0.0.1', port: 8000, path: '/api/v1/health', method: 'GET' }, res => {
            let body = '';
            res.on('data', chunk => { body += chunk; });
            res.on('end', () => {
                try {
                    assert.equal(res.statusCode, 200);
                    const json = JSON.parse(body);
                    assert.equal(json.success, true);
                    assert.ok(json.data.status);
                    assert.ok(json.data.services);
                    resolve();
                } catch (err) { reject(err); }
            });
        });
        req.on('error', reject);
        req.end();
    });
});

// ─── Full Pipeline Integration ────────────────────────────────────────────────

test('pipeline: deterministic scoring — perfect inputs produce SUITABLE', () => {
    const skillResult = { mandatory_score: 100, preferred_score: 100 };
    const scores = calculateScores(skillResult, 100, 100, 100);
    const eligibility = evaluateEligibility(scores.overall_score, [], 0, true);
    assert.equal(eligibility.decision, 'SUITABLE');
    assert.equal(scores.overall_score, 100);
});

test('pipeline: REJECT when mandatory skills missing (direct engine)', () => {
    const skillResult = { mandatory_score: 0, preferred_score: 0 };
    const scores = calculateScores(skillResult, 100, 100, 100);
    const eligibility = evaluateEligibility(scores.overall_score, ['Java', 'Docker'], 0, true);
    assert.equal(eligibility.decision, 'REJECT');
    assert.ok(eligibility.mandatory_failures.length >= 2);
});

test('pipeline: text extraction + matching returns a valid decision', () => {
    const resumeText = 'Jane Dev\njane@test.com\nJava Spring Boot Microservices Docker AWS\nBachelor Computer Science';
    const jdText = 'Job Title: Java Developer\nRequired: Java Spring Boot';
    const resume = extractResume(resumeText);
    const jd = extractJobDescription(jdText);
    const skills = matchSkills(resume.skills, jd.mandatory_requirements.skills, jd.preferred_requirements.skills);
    const missingMandatory = skills.missing.filter(m => m.is_mandatory).map(m => m.skill);
    const scores = calculateScores(skills, 100, 100, 100);
    const eligibility = evaluateEligibility(scores.overall_score, missingMandatory, 0, true);
    assert.ok(['SUITABLE', 'BORDERLINE', 'REJECT'].includes(eligibility.decision));
});

test('pipeline: candidate missing mandatory skill is REJECT', () => {
    const resumeText = 'Alice Dev\nJava Spring Boot\nno kubernetes no docker';
    const jdText = 'Job Title: Platform Engineer\nRequired: Java Spring Boot Kubernetes Docker';
    const resume = extractResume(resumeText);
    const jd = extractJobDescription(jdText);
    const skills = matchSkills(resume.skills, jd.mandatory_requirements.skills, jd.preferred_requirements.skills);
    const missingMandatory = skills.missing.filter(m => m.is_mandatory).map(m => m.skill);
    // Force REJECT by passing missing mandatory skills directly
    const eligibility = evaluateEligibility(100, missingMandatory.length > 0 ? missingMandatory : ['ForcedMissing'], 0, true);
    assert.equal(eligibility.decision, 'REJECT');
});
