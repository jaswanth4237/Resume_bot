const settings = require('../config/settings');
function evaluateEligibility(overallScore, missingMandatory, experienceGap, educationSatisfied) {
  const mandatoryFailures = missingMandatory.map(skill => `Missing mandatory skill: ${skill}`);
  const reasons = missingMandatory.map(skill => `Candidate lacks mandatory required skill '${skill}'.`);
  if (experienceGap > 0) { mandatoryFailures.push(`Experience gap: lacks ${experienceGap} years required minimum experience`); reasons.push(`Candidate falls short of minimum required experience by ${experienceGap} years.`); }
  if (!educationSatisfied) { mandatoryFailures.push('Mandatory education requirement not satisfied'); reasons.push('Candidate does not meet mandatory education criteria.'); }
  let decision;
  if (mandatoryFailures.length) decision = 'REJECT';
  else if (overallScore >= settings.suitableThreshold) decision = 'SUITABLE';
  else if (overallScore >= settings.borderlineThreshold) decision = 'BORDERLINE';
  else { decision = 'REJECT'; reasons.push(`Overall match score ${overallScore}% is below required cutoff of ${settings.borderlineThreshold}%.`); }
  return { decision, decision_reasons: reasons.length ? reasons : [`Candidate satisfies mandatory requirements and meets ${decision.toLowerCase()} score threshold.`], mandatory_failures: mandatoryFailures };
}
module.exports = { evaluateEligibility };
