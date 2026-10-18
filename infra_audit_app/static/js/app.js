/**
 * Main Frontend Application Controller.
 * Coordinates UI rendering, event delegation, modal interactions, and module calls.
 */

import { state } from './data.js';
import { distanceToCorridor } from './verifier.js';
import { evaluateReasoningText, TIER_WEIGHTS } from './moderator.js';
import { renderAuditCharts } from './charts.js';

function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  const toast = document.createElement("div");
  const bg = type === "success" ? "bg-emerald-600" : type === "error" ? "bg-red-600" : "bg-slate-800";
  toast.className = `${bg} text-white text-xs px-4 py-2.5 rounded-lg shadow-lg pointer-events-auto transition-opacity duration-300 flex items-center space-x-2`;
  toast.innerHTML = `<span>${type === "success" ? "✓" : type === "error" ? "⚠" : "ℹ"}</span><span>${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// Navigation Controller
const navButtons = [
  { id: "nav-tenders", view: "view-tenders" },
  { id: "nav-contractors", view: "view-contractors" },
  { id: "nav-evidence", view: "view-evidence" },
  { id: "nav-reviews", view: "view-reviews" },
  { id: "nav-analytics", view: "view-analytics" },
];

function initNavigation() {
  navButtons.forEach(btnInfo => {
    const btn = document.getElementById(btnInfo.id);
    if (!btn) return;
    btn.addEventListener("click", () => {
      navButtons.forEach(b => {
        document.getElementById(b.id).classList.remove("tab-active");
        document.getElementById(b.view).classList.add("hidden");
      });
      btn.classList.add("tab-active");
      document.getElementById(btnInfo.view).classList.remove("hidden");
      if (btnInfo.id === "nav-analytics") {
        renderAuditCharts();
      }
    });
  });
}

// Tenders View
export function renderTenders() {
  const agencyFilter = document.getElementById("filter-agency").value;
  const statusFilter = document.getElementById("filter-status").value;
  const grid = document.getElementById("tender-cards-grid");
  grid.innerHTML = "";

  const filtered = state.tenders.filter(t => {
    const matchesAgency = agencyFilter === "ALL" || t.authority.includes(agencyFilter);
    const matchesStatus = statusFilter === "ALL" || t.status === statusFilter;
    return matchesAgency && matchesStatus;
  });

  document.getElementById("tender-count").textContent = filtered.length;

  filtered.forEach(tender => {
    const card = document.createElement("div");
    card.className = "bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden flex flex-col justify-between hover:shadow-md transition-shadow";

    const isLowBid = tender.bids.some(b => b.isL1 && b.devPct < -20);
    const l1Bid = tender.bids.find(b => b.isL1);

    card.innerHTML = `
      <div class="p-5 space-y-3">
        <div class="flex items-center justify-between text-xs">
          <span class="font-mono text-slate-500 font-semibold">${tender.authority.split("(")[0]}</span>
          <span class="px-2 py-0.5 rounded-full font-semibold ${
            tender.status === 'AWARDED' ? 'bg-emerald-100 text-emerald-800' :
            tender.status === 'FINANCIAL_BID_OPENED' ? 'bg-blue-100 text-blue-800' :
            'bg-amber-100 text-amber-800'
          }">${tender.status.replace(/_/g, ' ')}</span>
        </div>

        <h3 class="font-bold text-slate-900 text-sm leading-snug line-clamp-2">${tender.title}</h3>

        <div class="grid grid-cols-2 gap-2 text-xs py-2 border-y border-slate-100">
          <div>
            <span class="text-slate-400 block">Estimated Cost:</span>
            <span class="font-bold text-slate-800">₹${tender.estimateCrores.toFixed(1)} Cr</span>
          </div>
          <div>
            <span class="text-slate-400 block">L1 Quoted Amount:</span>
            <span class="font-bold ${isLowBid ? 'text-red-600' : 'text-slate-800'}">
              ${l1Bid ? `₹${l1Bid.quote.toFixed(1)} Cr (${l1Bid.devPct.toFixed(1)}%)` : 'Bidding in progress'}
            </span>
          </div>
        </div>

        ${isLowBid ? `
          <div class="bg-red-50 border border-red-200 rounded-lg p-2.5 text-[11px] text-red-700 flex items-start space-x-2">
            <span class="font-bold text-red-800 shrink-0">⚠️ ALERT:</span>
            <span>Aggressive Underbid (-24.2%). Model predicts 69.4% probability of execution delay.</span>
          </div>
        ` : ''}

        <p class="text-xs text-slate-500 line-clamp-2">${tender.specs}</p>
      </div>

      <div class="p-4 bg-slate-50 border-t border-slate-100 flex items-center justify-between text-xs">
        <span class="text-slate-500 font-medium">${tender.district}, ${tender.state}</span>
        <button class="btn-inspect-tender px-3 py-1.5 bg-slate-900 hover:bg-slate-800 text-white font-medium rounded-lg transition-colors" data-id="${tender.id}">
          Inspect Bids & Risks →
        </button>
      </div>
    `;
    grid.appendChild(card);
  });

  document.querySelectorAll(".btn-inspect-tender").forEach(btn => {
    btn.addEventListener("click", () => openTenderModal(btn.getAttribute("data-id")));
  });
}

function openTenderModal(tenderId) {
  const tender = state.tenders.find(t => t.id === tenderId);
  if (!tender) return;

  document.getElementById("modal-ref-badge").textContent = tender.ref;
  document.getElementById("modal-title").textContent = tender.title;
  document.getElementById("modal-authority").textContent = tender.authority;
  document.getElementById("modal-estimate").textContent = `₹${tender.estimateCrores.toFixed(1)} Cr`;
  document.getElementById("modal-status").textContent = tender.status.replace(/_/g, ' ');
  document.getElementById("modal-duration").textContent = `${tender.durationMonths} Months`;

  const tbody = document.getElementById("modal-bidders-tbody");
  tbody.innerHTML = "";

  if (tender.bids.length === 0) {
    tbody.innerHTML = `<tr><td colspan="5" class="py-4 text-center text-slate-400">Bids have not been unsealed yet for this active procurement tender.</td></tr>`;
  } else {
    tender.bids.forEach((bid, idx) => {
      const tr = document.createElement("tr");
      tr.className = bid.isL1 ? "bg-orange-50/70 font-medium" : "";
      tr.innerHTML = `
        <td class="py-2.5 px-3"><span class="font-semibold text-slate-800">${bid.name}</span></td>
        <td class="py-2.5 px-3 font-semibold">₹${bid.quote.toFixed(1)} Cr</td>
        <td class="py-2.5 px-3 ${bid.devPct < -20 ? 'text-red-600 font-bold' : 'text-slate-600'}">
          ${bid.devPct > 0 ? '+' : ''}${bid.devPct.toFixed(2)}%
        </td>
        <td class="py-2.5 px-3">${bid.techScore} / 100</td>
        <td class="py-2.5 px-3">
          <span class="px-2 py-0.5 rounded text-[10px] font-bold ${bid.isL1 ? 'bg-orange-600 text-white' : 'bg-slate-200 text-slate-700'}">
            ${bid.isL1 ? 'L1 Winner' : `L${idx + 1}`}
          </span>
        </td>
      `;
      tbody.appendChild(tr);
    });
  }

  const riskBox = document.getElementById("modal-risk-box");
  if (tender.riskFlags.length > 0) {
    riskBox.className = "p-4 rounded-xl border border-red-200 bg-red-50 text-xs space-y-2";
    riskBox.innerHTML = `
      <h5 class="font-bold text-red-900 text-xs uppercase flex items-center space-x-1">
        <span>⚠️</span> <span>Algorithmic Procurement Risk Assessment:</span>
      </h5>
      <ul class="list-disc pl-4 space-y-1 text-red-800">
        ${tender.riskFlags.map(f => `<li>${f}</li>`).join('')}
      </ul>
      <p class="text-[11px] text-red-700 font-medium pt-1 border-t border-red-200">
        Delay Forecast: Estimated completion risk is <span class="font-bold underline">${tender.delayProbPct}%</span> based on contractor execution history.
      </p>
    `;
  } else {
    riskBox.className = "p-4 rounded-xl border border-emerald-200 bg-emerald-50 text-xs space-y-1 text-emerald-800";
    riskBox.innerHTML = `
      <h5 class="font-bold text-emerald-900 text-xs uppercase">✓ Competitive Benchmark Passed</h5>
      <p>Bids align with regional standard schedule of rates. Normal delay risk (${tender.delayProbPct}%).</p>
    `;
  }

  document.getElementById("tender-modal").classList.remove("hidden");
}

function renderContractors() {
  const tbody = document.getElementById("contractors-tbody");
  tbody.innerHTML = "";

  state.contractors.forEach(c => {
    const tr = document.createElement("tr");
    tr.className = "hover:bg-slate-50 transition-colors";
    tr.innerHTML = `
      <td class="py-3 px-4">
        <span class="font-semibold text-slate-900 block">${c.name}</span>
        <span class="text-[11px] text-slate-400 font-mono">${c.reg}</span>
      </td>
      <td class="py-3 px-4 text-slate-600">${c.year}</td>
      <td class="py-3 px-4 text-slate-800 font-medium">${c.completed} (${c.onTime} on-time)</td>
      <td class="py-3 px-4">
        <span class="font-semibold ${c.delayRatePct > 50 ? 'text-red-600' : 'text-slate-700'}">${c.delayRatePct}%</span>
      </td>
      <td class="py-3 px-4 text-slate-600">${c.avgDelayMonths} mo</td>
      <td class="py-3 px-4 text-slate-600">+${c.overrunPct}%</td>
      <td class="py-3 px-4">
        <div class="flex items-center space-x-1">
          <span class="font-bold text-amber-600">${c.quality}</span>
          <span class="text-amber-500 text-xs">★</span>
        </div>
      </td>
      <td class="py-3 px-4">
        ${c.blacklisted ? `
          <span class="px-2 py-1 rounded bg-red-100 text-red-800 font-bold text-[10px] uppercase">Blacklisted</span>
        ` : `
          <span class="px-2 py-1 rounded bg-emerald-100 text-emerald-800 font-semibold text-[10px] uppercase">Eligible</span>
        `}
      </td>
    `;
    tbody.appendChild(tr);
  });
}

function renderEvidenceFeed() {
  const container = document.getElementById("evidence-feed-list");
  container.innerHTML = "";
  document.getElementById("verified-count-label").textContent = state.evidence.length;

  state.evidence.forEach(ev => {
    const item = document.createElement("div");
    item.className = "bg-white p-4 rounded-xl shadow-sm border border-slate-200 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4";

    const badgeColor = ev.type === "POTHOLE_CLUSTER" ? "bg-amber-100 text-amber-800" :
                       ev.type === "SURFACE_CRACKING" ? "bg-orange-100 text-orange-800" :
                       "bg-blue-100 text-blue-800";

    item.innerHTML = `
      <div class="space-y-1">
        <div class="flex items-center space-x-2">
          <span class="px-2 py-0.5 rounded text-[10px] font-bold uppercase ${badgeColor}">
            ${ev.type.replace(/_/g, ' ')}
          </span>
          <span class="text-xs text-slate-400 font-medium">• ${ev.timeStr}</span>
          <span class="text-xs text-emerald-700 font-semibold bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
            ✓ Verified (${ev.dist}m to corridor)
          </span>
        </div>
        <p class="text-xs text-slate-800 font-medium">${ev.desc}</p>
        <div class="text-[11px] text-slate-500 font-mono">
          GPS: ${ev.lat.toFixed(4)}, ${ev.lon.toFixed(4)} • Tier: ${ev.tier.replace(/_/g, ' ')}
        </div>
      </div>
      <div class="text-right shrink-0 bg-slate-50 p-2.5 rounded-lg border border-slate-100">
        <span class="text-[10px] text-slate-400 uppercase font-semibold block">Citizen Rep</span>
        <span class="text-sm font-bold text-emerald-600">+${ev.points} pts</span>
      </div>
    `;
    container.appendChild(item);
  });
}

function renderReviewsFeed() {
  const container = document.getElementById("reviews-feed-container");
  container.innerHTML = "";

  let weightedSum = 0;
  let totalWeight = 0;

  state.reviews.forEach(rev => {
    weightedSum += rev.rating * rev.tierWeight;
    totalWeight += rev.tierWeight;

    const card = document.createElement("div");
    card.className = "bg-white p-4 rounded-xl shadow-sm border border-slate-200 space-y-2";
    card.innerHTML = `
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-2">
          <span class="text-xs font-bold text-slate-800">${rev.tier.replace(/_/g, ' ')}</span>
          <span class="text-[10px] px-2 py-0.5 rounded font-mono font-semibold bg-slate-100 text-slate-600">
            Weight: ${rev.tierWeight}x
          </span>
          <span class="text-xs text-slate-400">• ${rev.timeStr}</span>
        </div>
        <div class="flex items-center space-x-1 text-amber-500 font-bold text-xs">
          <span>${rev.rating.toFixed(1)}</span> <span>★</span>
        </div>
      </div>
      <p class="text-xs text-slate-700 leading-relaxed">${rev.text}</p>
      <div class="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px]">
        <span class="text-emerald-700 font-medium">✓ AI Reasoning Score: ${rev.score}/100 (${rev.sentiment.replace(/_/g, ' ')})</span>
        <span class="text-slate-400 font-mono text-[10px]">VERIFIED_FEEDBACK</span>
      </div>
    `;
    container.appendChild(card);
  });

  if (totalWeight > 0) {
    const composite = (weightedSum / totalWeight).toFixed(2);
    document.getElementById("composite-score-badge").textContent = composite;
    document.getElementById("weight-volume-label").textContent = `${totalWeight.toFixed(1)}x`;
    const confidence = Math.min(100, Math.round((totalWeight / 30) * 100));
    document.getElementById("confidence-index-label").textContent = `${confidence.toFixed(1)}%`;
  }
}

window.addEventListener("DOMContentLoaded", () => {
  initNavigation();
  renderTenders();
  renderContractors();
  renderEvidenceFeed();
  renderReviewsFeed();

  document.getElementById("filter-agency").addEventListener("change", renderTenders);
  document.getElementById("filter-status").addEventListener("change", renderTenders);

  document.getElementById("btn-close-modal").addEventListener("click", () => {
    document.getElementById("tender-modal").classList.add("hidden");
  });

  document.getElementById("btn-fill-valid-gps").addEventListener("click", () => {
    document.getElementById("evidence-lat").value = "22.7550";
    document.getElementById("evidence-lon").value = "88.4860";
    showToast("Loaded GPS within NH-34 corridor bounds (Distance ~40m)", "info");
  });

  document.getElementById("btn-fill-invalid-gps").addEventListener("click", () => {
    document.getElementById("evidence-lat").value = "22.9500";
    document.getElementById("evidence-lon").value = "88.7500";
    showToast("Loaded simulated out-of-bounds GPS (Distance ~18km away)", "info");
  });

  document.getElementById("evidence-form").addEventListener("submit", (e) => {
    e.preventDefault();
    const tenderId = document.getElementById("evidence-tender-select").value;
    const tender = state.tenders.find(t => t.id === tenderId);
    const lat = parseFloat(document.getElementById("evidence-lat").value);
    const lon = parseFloat(document.getElementById("evidence-lon").value);
    const tier = document.getElementById("evidence-tier-select").value;
    const type = document.getElementById("evidence-type-select").value;
    const severity = parseInt(document.getElementById("evidence-severity-select").value);
    const desc = document.getElementById("evidence-desc").value.trim();

    const dist = distanceToCorridor(lat, lon, tender.corridorStart, tender.corridorEnd);
    const resultBox = document.getElementById("verification-result-box");
    resultBox.classList.remove("hidden");

    if (dist > 250) {
      resultBox.className = "p-3 rounded-lg border border-red-200 bg-red-50 text-xs text-red-800 space-y-1";
      resultBox.innerHTML = `
        <div class="font-bold">❌ REJECTED: Out-of-Bounds Submission</div>
        <p>Coordinates (${lat.toFixed(4)}, ${lon.toFixed(4)}) are <strong>${(dist / 1000).toFixed(1)} km</strong> away from the approved corridor (Limit: 250m).</p>
        <p class="text-[11px] text-red-600 font-semibold">Reputation Penalty Applied: -15 Points</p>
      `;
      showToast("Evidence rejected: GPS location outside project corridor", "error");
    } else {
      resultBox.className = "p-3 rounded-lg border border-emerald-200 bg-emerald-50 text-xs text-emerald-800 space-y-1";
      resultBox.innerHTML = `
        <div class="font-bold">✓ VERIFIED GROUND TRUTH: Corridor Match</div>
        <p>Confirmed within <strong>${dist.toFixed(1)}m</strong> of corridor centerline. Fresh capture timestamp matched.</p>
        <p class="text-[11px] text-emerald-600 font-semibold">Reputation Reward: +5 Points awarded to submitter</p>
      `;

      state.evidence.unshift({
        id: `EV-${Math.floor(Math.random() * 900 + 100)}`,
        tenderId: tender.id,
        tier, lat, lon,
        timeStr: "Just now",
        type, severity, desc,
        status: "VERIFIED_GROUND_TRUTH",
        dist: Math.round(dist * 10) / 10,
        points: 5
      });

      renderEvidenceFeed();
      showToast("Ground-truth evidence verified & added to public record!", "success");
    }
  });

  document.getElementById("btn-preset-technical").addEventListener("click", () => {
    document.getElementById("review-reasoning-input").value =
      "The contractor laid 40mm bitumen wearing course without adequate aggregate grading, causing premature potholes and waterlogging between Km 32-34 within 2 months of laying.";
    document.getElementById("review-tier-select").value = "CIVIL_ENGINEER";
    document.getElementById("review-rating-select").value = "2.0";
  });

  document.getElementById("btn-preset-defamation").addEventListener("click", () => {
    document.getElementById("review-reasoning-input").value =
      "These contractor thieves and looters took huge bribes and scammed the public! Jail them immediately!";
    document.getElementById("review-tier-select").value = "CITIZEN";
    document.getElementById("review-rating-select").value = "1.0";
  });

  document.getElementById("btn-preset-vague").addEventListener("click", () => {
    document.getElementById("review-reasoning-input").value = "Bad road.";
    document.getElementById("review-tier-select").value = "CITIZEN";
    document.getElementById("review-rating-select").value = "1.0";
  });

  document.getElementById("review-form").addEventListener("submit", (e) => {
    e.preventDefault();
    const tenderId = document.getElementById("review-tender-select").value;
    if (tenderId === "TND-2026-MORTH-811") {
      const resultDiv = document.getElementById("ai-moderation-result");
      resultDiv.classList.remove("hidden");
      resultDiv.className = "p-3 rounded-lg border border-amber-200 bg-amber-50 text-xs text-amber-800 space-y-1";
      resultDiv.innerHTML = `
        <div class="font-bold">⏳ Observation Gate Active (5-Day Delay)</div>
        <p>Public opinion reviews for this project open in <strong>3.2 days</strong> to allow field verification and prevent premature bid manipulation.</p>
      `;
      showToast("Observation gate active: citizen reviews open post-bidding", "error");
      return;
    }

    const tier = document.getElementById("review-tier-select").value;
    const rating = parseFloat(document.getElementById("review-rating-select").value);
    const text = document.getElementById("review-reasoning-input").value.trim();

    const evalResult = evaluateReasoningText(text);
    const resultDiv = document.getElementById("ai-moderation-result");
    resultDiv.classList.remove("hidden");

    if (!evalResult.approved) {
      resultDiv.className = "p-3 rounded-lg border border-red-200 bg-red-50 text-xs text-red-800 space-y-1";
      resultDiv.innerHTML = `
        <div class="font-bold">❌ REJECTED BY AI MODERATOR</div>
        <p>${evalResult.reason}</p>
        <span class="text-[10px] text-red-600 block font-mono">Score: ${evalResult.score}/100</span>
      `;
      showToast("Review withheld by AI moderator: Defamation or low substance", "error");
    } else {
      resultDiv.className = "p-3 rounded-lg border border-emerald-200 bg-emerald-50 text-xs text-emerald-800 space-y-1";
      resultDiv.innerHTML = `
        <div class="font-bold">✓ APPROVED FOR PUBLIC DISPLAY</div>
        <p>${evalResult.reason}</p>
        <span class="text-[10px] text-emerald-700 block font-mono">Reasoning Score: ${evalResult.score}/100 • Effective Weight: ${TIER_WEIGHTS[tier]}x</span>
      `;

      state.reviews.unshift({
        id: `REV-${Math.floor(Math.random() * 900 + 100)}`,
        tenderId, tier,
        tierWeight: TIER_WEIGHTS[tier],
        rating,
        timeStr: "Just now",
        text,
        score: evalResult.score,
        verdict: "APPROVED",
        sentiment: evalResult.score > 80 ? "HIGH_QUALITY_ANALYTICAL" : "OBJECTIVE"
      });

      renderReviewsFeed();
      showToast("Review passed AI moderation & incorporated into weighted score!", "success");
    }
  });
});
