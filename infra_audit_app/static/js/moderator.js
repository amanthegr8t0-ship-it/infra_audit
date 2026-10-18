/**
 * Client-side AI Reasoning Quality & Anti-Defamation Evaluator.
 * Mirrors backend `services/ai_moderator.py` logic.
 */

export const TIER_WEIGHTS = {
  CITIZEN: 1.0,
  CIVIL_ENGINEER: 5.0,
  ROAD_QUALITY_INSPECTOR: 8.0,
  STRUCTURAL_ENGINEER: 10.0
};

export function evaluateReasoningText(text) {
  const lower = text.toLowerCase();
  const defamationTerms = [
    "thieves", "chor", "looters", "scammers", "criminals",
    "jail them", "frauds", "bribe", "corrupt dogs"
  ];
  const technicalTerms = [
    "bitumen", "tar", "asphalt", "aggregate", "drainage",
    "pothole", "cracks", "sub-base", "thickness", "slope",
    "delay", "roller", "monsoon", "culvert"
  ];

  const hasDefamation = defamationTerms.some(term => lower.includes(term));
  const matchedTech = technicalTerms.filter(term => lower.includes(term));
  const words = lower.trim().split(/\s+/).length;

  let score = Math.min(40, words * 1.5) + Math.min(40, matchedTech.length * 15);
  if (hasDefamation) score = Math.max(0, score - 70);

  if (hasDefamation) {
    return {
      approved: false,
      score: 0.0,
      verdict: "REJECTED",
      reason: "Defamatory allegations detected without verified technical evidence. Slanderous statements violate governance policies."
    };
  }
  if (score < 40) {
    return {
      approved: false,
      score: Math.round(score),
      verdict: "REJECTED",
      reason: "Feedback is overly vague or emotional. Please cite specific roadway observations, materials, or contractor execution parameters."
    };
  }
  return {
    approved: true,
    score: Math.min(100, Math.round(score)),
    verdict: "APPROVED",
    reason: `Substantive technical feedback approved! Cites relevant engineering indicators (${matchedTech.slice(0, 3).join(', ')}).`
  };
}
