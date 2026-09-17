function calculateScores(skillResult, experienceScore, responsibilitiesScore, educationScore) {
  const skills = Number(((skillResult.mandatory_score * 0.8) + (skillResult.preferred_score * 0.2)).toFixed(2));
  const categoryScores = { skills, experience: Number(experienceScore.toFixed(2)), responsibilities: Number(responsibilitiesScore.toFixed(2)), education: Number(educationScore.toFixed(2)), preferred: skillResult.preferred_score };
  const overall = Math.min(100, Math.max(0, Number((skills * 0.5 + experienceScore * 0.2 + responsibilitiesScore * 0.15 + educationScore * 0.05 + skillResult.preferred_score * 0.1).toFixed(2))));
  return { overall_score: overall, category_scores: categoryScores };
}
module.exports = { calculateScores };
