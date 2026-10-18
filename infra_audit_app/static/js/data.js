/**
 * Initial application state and seed data for client-side fallback / standalone mode.
 * When connected to the FastAPI backend (`uvicorn main:app`), the client fetches live
 * records from `/api/tenders`, `/api/contractors`, `/api/evidence`, and `/api/reviews`.
 */
export const state = {
  tenders: [
    {
      id: "TND-2026-NHAI-091",
      ref: "NHAI/RO-KOL/NH-34/4L/2026/091",
      title: "4-Laning of NH-34 Stretch (Barasat to Krishnanagar Km 28.000 to Km 54.000)",
      authority: "National Highways Authority of India (NHAI)",
      category: "HIGHWAY",
      state: "West Bengal",
      district: "North 24 Parganas & Nadia",
      corridorStart: { lat: 22.7210, lon: 88.4820 },
      corridorEnd: { lat: 23.4010, lon: 88.5020 },
      estimateCrores: 425.0,
      durationMonths: 30,
      status: "AWARDED",
      bids: [
        { bidderId: "CONT-002", name: "Apex Highway & Metro Builders", quote: 322.0, techScore: 78.5, isL1: true, devPct: -24.24 },
        { bidderId: "CONT-001", name: "Eastern Infracon Projects Ltd", quote: 398.0, techScore: 94.0, isL1: false, devPct: -6.35 },
        { bidderId: "CONT-004", name: "Bengal State Roads & Civil Infra", quote: 412.0, techScore: 89.5, isL1: false, devPct: -3.06 }
      ],
      riskFlags: [
        "ABNORMALLY_LOW_BID: L1 quote (₹322.00 Cr) is 24.2% below official engineer estimate. High probability of sub-base thickness reduction and liquidity stress."
      ],
      delayProbPct: 69.4,
      specs: "Bituminous Concrete (BC) 50mm over Dense Bituminous Macadam (DBM) 100mm, with 6 underpasses and storm water box drains."
    },
    {
      id: "TND-2026-PWD-404",
      ref: "WB/PWD/KOL/FLY/2026/04",
      title: "Construction of 4-Lane Elevated Corridor on EM Bypass connecting New Town Connector",
      authority: "West Bengal Public Works Department (WB PWD)",
      category: "FLYOVER",
      state: "West Bengal",
      district: "Kolkata",
      corridorStart: { lat: 22.5180, lon: 88.3990 },
      corridorEnd: { lat: 22.5690, lon: 88.4320 },
      estimateCrores: 280.0,
      durationMonths: 24,
      status: "FINANCIAL_BID_OPENED",
      bids: [
        { bidderId: "CONT-001", name: "Eastern Infracon Projects Ltd", quote: 271.5, techScore: 92.0, isL1: true, devPct: -3.04 },
        { bidderId: "CONT-004", name: "Bengal State Roads & Civil Infra", quote: 276.0, techScore: 90.0, isL1: false, devPct: -1.43 }
      ],
      riskFlags: [],
      delayProbPct: 18.5,
      specs: "Pre-stressed concrete (PSC) I-girders with elastomeric bearings and noise barriers across residential sectors."
    },
    {
      id: "TND-2026-MORTH-811",
      ref: "MoRTH/BR/TEESTA/2026/811",
      title: "High-Level 4-Lane Bridge over River Teesta with Approaches on NH-31D",
      authority: "Ministry of Road Transport and Highways (MoRTH)",
      category: "BRIDGE",
      state: "West Bengal",
      district: "Jalpaiguri",
      corridorStart: { lat: 26.5400, lon: 88.7100 },
      corridorEnd: { lat: 26.5650, lon: 88.7350 },
      estimateCrores: 560.0,
      durationMonths: 36,
      status: "PUBLISHED_BIDDING",
      bids: [],
      riskFlags: ["Bidding active. Citizen review observation window gated until bid opening."],
      delayProbPct: 25.0,
      specs: "Cable-stayed navigation span with seismic dampers and deep well foundation in active alluvial riverbed."
    }
  ],
  contractors: [
    {
      id: "CONT-001",
      name: "Eastern Infracon Projects Ltd",
      reg: "ROC-WB-98231",
      year: 2008,
      completed: 18,
      onTime: 15,
      delayRatePct: 16.6,
      avgDelayMonths: 2.4,
      overrunPct: 4.2,
      quality: 4.3,
      blacklisted: false
    },
    {
      id: "CONT-002",
      name: "Apex Highway & Metro Builders",
      reg: "ROC-DL-44129",
      year: 2014,
      completed: 12,
      onTime: 5,
      delayRatePct: 58.3,
      avgDelayMonths: 8.5,
      overrunPct: 19.4,
      quality: 2.7,
      blacklisted: false
    },
    {
      id: "CONT-003",
      name: "Vistara Structural Bridges Corp",
      reg: "ROC-MH-77182",
      year: 2011,
      completed: 9,
      onTime: 2,
      delayRatePct: 77.8,
      avgDelayMonths: 14.0,
      overrunPct: 34.0,
      quality: 1.4,
      blacklisted: true,
      blacklistReason: "Disqualified by MoRTH for catastrophic girder sag due to substandard grade concrete."
    },
    {
      id: "CONT-004",
      name: "Bengal State Roads & Civil Infra",
      reg: "ROC-WB-11209",
      year: 2003,
      completed: 26,
      onTime: 21,
      delayRatePct: 19.2,
      avgDelayMonths: 3.1,
      overrunPct: 6.5,
      quality: 4.1,
      blacklisted: false
    }
  ],
  evidence: [
    {
      id: "EV-901",
      tenderId: "TND-2026-NHAI-091",
      tier: "CITIZEN",
      lat: 22.7420,
      lon: 88.4845,
      timeStr: "14 hours ago",
      type: "POTHOLE_CLUSTER",
      severity: 4,
      desc: "Deep crater-like potholes recurring at Km 31 marker right after light rain. Sub-base aggregate visibly exposed.",
      status: "VERIFIED_GROUND_TRUTH",
      dist: 42.0,
      points: 5
    },
    {
      id: "EV-902",
      tenderId: "TND-2026-NHAI-091",
      tier: "CIVIL_ENGINEER",
      lat: 22.8105,
      lon: 88.4910,
      timeStr: "28 hours ago",
      type: "SURFACE_CRACKING",
      severity: 3,
      desc: "Longitudinal surface cracking detected along 200m section. Indicates inadequate bitumen binder grade or delayed compaction.",
      status: "VERIFIED_GROUND_TRUTH",
      dist: 35.5,
      points: 5
    }
  ],
  reviews: [
    {
      id: "REV-01",
      tenderId: "TND-2026-NHAI-091",
      tier: "CIVIL_ENGINEER",
      tierWeight: 5.0,
      rating: 2.0,
      timeStr: "Yesterday",
      text: "Apex Builders quoted -24% below the MoRTH standard schedule of rates. At this margin, they cannot procure VG-30 grade bitumen and have omitted necessary cross-drainage culverts between Km 32-35, leading to immediate waterlogging.",
      score: 92.0,
      verdict: "APPROVED",
      sentiment: "HIGH_QUALITY_ANALYTICAL"
    },
    {
      id: "REV-02",
      tenderId: "TND-2026-NHAI-091",
      tier: "CITIZEN",
      tierWeight: 1.0,
      rating: 1.5,
      timeStr: "8 hours ago",
      text: "The road surface at the Barasat junction is already peeling off just two weeks after initial tarring. Loose aggregate stones are flying into commuter windshields.",
      score: 78.0,
      verdict: "APPROVED",
      sentiment: "OBJECTIVE"
    }
  ]
};
