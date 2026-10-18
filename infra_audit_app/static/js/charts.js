/**
 * Analytics Charts Module using Chart.js.
 * Renders Bid Discount vs. Delay Probability and Multi-Tier Governance Weights.
 */

let chartRiskInstance = null;
let chartTierInstance = null;

export function renderAuditCharts() {
  const ctxRisk = document.getElementById("chart-bid-risk");
  if (ctxRisk) {
    if (chartRiskInstance) chartRiskInstance.destroy();
    chartRiskInstance = new Chart(ctxRisk, {
      type: "bar",
      data: {
        labels: [
          "Apex Highway (-24.2% Underbid)",
          "Eastern Infracon (-6.4%)",
          "Bengal State Roads (-3.1%)"
        ],
        datasets: [
          {
            label: "Quoted Price vs Estimate (Crores ₹)",
            data: [322.0, 398.0, 412.0],
            backgroundColor: "#3b82f6",
            yAxisID: "y"
          },
          {
            label: "Predicted Delay Probability (%)",
            data: [69.4, 16.6, 19.2],
            backgroundColor: "#ef4444",
            yAxisID: "y1"
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            type: "linear",
            position: "left",
            title: { display: true, text: "Bid Value (₹ Cr)", font: { size: 10 } }
          },
          y1: {
            type: "linear",
            position: "right",
            grid: { drawOnChartArea: false },
            title: { display: true, text: "Delay Risk (%)", font: { size: 10 } }
          }
        },
        plugins: {
          legend: { position: "top", labels: { boxWidth: 12, font: { size: 11 } } }
        }
      }
    });
  }

  const ctxTier = document.getElementById("chart-tier-weights");
  if (ctxTier) {
    if (chartTierInstance) chartTierInstance.destroy();
    chartTierInstance = new Chart(ctxTier, {
      type: "doughnut",
      data: {
        labels: [
          "Structural Engineer (10x)",
          "Road Inspector (8x)",
          "Civil Engineer (5x)",
          "Citizen (1x)"
        ],
        datasets: [
          {
            data: [10, 8, 5, 1],
            backgroundColor: ["#6366f1", "#0ea5e9", "#10b981", "#f59e0b"]
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "bottom", labels: { boxWidth: 12, font: { size: 11 } } }
        }
      }
    });
  }
}
