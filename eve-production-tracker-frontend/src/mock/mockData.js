// This is a plain JavaScript file for exporting data.
// It should not contain a function like _getMockData().

const now = new Date();
const addHours = (date, h) => new Date(date.getTime() + h * 3600 * 1000);

export const mockCharacters = [
  { character_id: 90000001, character_name: "Industrialist Prime" },
  { character_id: 90000002, character_name: "Dr. Research" },
  { character_id: 90000003, character_name: "Captain Copy" },
  { character_id: 90000004, character_name: "Reaction Specialist" },
  { character_id: 90000005, character_name: "Planet Harvester" },
  { character_id: 90000006, character_name: "Veteran Producer" },
  { character_id: 90000007, character_name: "Invention Guru" },
  { character_id: 90000008, character_name: "Lazy Spacer" },
  { character_id: 90000009, character_name: "Newbie Industrialist" },
  { character_id: 90000010, character_name: "Corp CEO" },
  { character_id: 90000011, character_name: "Galaxy Wanderer" },
  { character_id: 90000012, character_name: "Blueprint Farmer" },
];

export const mockActivities = {
  90000001: {
    lines: {
      manufacturing: { total: 11, used: 3 },
      research: { total: 10, used: 1 },
      reactions: { total: 2, used: 1 },
    },
    planets: { total: 6, used: 5 },
  },
  90000002: {
    lines: {
      manufacturing: { total: 5, used: 0 },
      research: { total: 11, used: 2 },
      reactions: { total: 3, used: 0 },
    },
    planets: { total: 6, used: 6 },
  },
  90000003: {
    lines: {
      manufacturing: { total: 8, used: 1 },
      research: { total: 8, used: 4 },
      reactions: { total: 1, used: 0 },
    },
    planets: { total: 5, used: 5 },
  },
  90000004: {
    lines: {
      manufacturing: { total: 2, used: 0 },
      research: { total: 1, used: 0 },
      reactions: { total: 5, used: 2 },
    },
    planets: { total: 5, used: 4 },
  },
  90000005: {
    lines: {
      manufacturing: { total: 1, used: 0 },
      research: { total: 1, used: 0 },
      reactions: { total: 0, used: 0 },
    },
    planets: { total: 6, used: 6 },
  },
  90000006: {
    lines: {
      manufacturing: { total: 11, used: 5 },
      research: { total: 11, used: 0 },
      reactions: { total: 4, used: 0 },
    },
    planets: { total: 6, used: 3 },
  },
  90000007: {
    lines: {
      manufacturing: { total: 1, used: 1 },
      research: { total: 8, used: 1 },
      reactions: { total: 0, used: 0 },
    },
    planets: { total: 5, used: 5 },
  },
  90000008: {
    lines: {
      manufacturing: { total: 1, used: 0 },
      research: { total: 1, used: 0 },
      reactions: { total: 0, used: 0 },
    },
    planets: { total: 2, used: 0 },
  },
  90000009: {
    lines: {
      manufacturing: { total: 1, used: 1 },
      research: { total: 0, used: 0 },
      reactions: { total: 0, used: 0 },
    },
    planets: { total: 3, used: 1 },
  },
  90000010: {
    lines: {
      manufacturing: { total: 11, used: 0 },
      research: { total: 11, used: 0 },
      reactions: { total: 5, used: 0 },
    },
    planets: { total: 6, used: 0 },
  },
  90000011: {
    lines: {
      manufacturing: { total: 1, used: 0 },
      research: { total: 1, used: 0 },
      reactions: { total: 0, used: 0 },
    },
    planets: { total: 2, used: 0 },
  },
  90000012: {
    lines: {
      manufacturing: { total: 1, used: 0 },
      research: { total: 1, used: 0 },
      reactions: { total: 0, used: 0 },
    },
    planets: { total: 2, used: 0 },
  },
};

export const mockJobs = {
  90000001: [
    {
      job_id: 1,
      product_name: "Tritanium",
      activity_id: 1,
      start_date: addHours(now, -2),
      end_date: addHours(now, 2),
      location_name: "Jita IV",
      status: "in-progress",
    },
    {
      job_id: 2,
      product_name: "Isogen",
      activity_id: 1,
      start_date: addHours(now, -1),
      end_date: addHours(now, 3),
      location_name: "Jita IV",
      status: "in-progress",
    },
    {
      job_id: 3,
      product_name: "Pyerite",
      activity_id: 1,
      start_date: addHours(now, 4),
      end_date: addHours(now, 7),
      location_name: "Amarr VIII",
      status: "in-progress",
    },
    {
      job_id: 4,
      product_name: "Veldspar BPC (Copy)",
      activity_id: 3,
      start_date: addHours(now, 0),
      end_date: addHours(now, 5),
      location_name: "Jita IV",
      status: "in-progress",
    },
    {
      job_id: 8,
      product_name: "Water (Reaction)",
      activity_id: 6,
      start_date: addHours(now, 2.5),
      end_date: addHours(now, 4.5),
      location_name: "Structure 1",
      status: "in-progress",
    },
  ],
  90000002: [
    {
      job_id: 5,
      product_name: "Cyno Field BPO (ME)",
      activity_id: 4,
      start_date: addHours(now, -10),
      end_date: addHours(now, 10),
      location_name: "Rens VI",
      status: "in-progress",
    },
    {
      job_id: 6,
      product_name: "Jump Drive BPO (TE)",
      activity_id: 5,
      start_date: addHours(now, -8),
      end_date: addHours(now, 12),
      location_name: "Rens VI",
      status: "paused",
    },
  ],
  90000003: [
    {
      job_id: 9,
      product_name: "Rifter BPC (Copy)",
      activity_id: 3,
      start_date: addHours(now, -20),
      end_date: addHours(now, 4),
      status: "in-progress",
    },
    {
      job_id: 10,
      product_name: "Rifter BPC (Copy)",
      activity_id: 3,
      start_date: addHours(now, -20),
      end_date: addHours(now, 4),
      status: "in-progress",
    },
    {
      job_id: 11,
      product_name: "Rifter BPC (Copy)",
      activity_id: 3,
      start_date: addHours(now, -20),
      end_date: addHours(now, 4),
      status: "in-progress",
    },
    {
      job_id: 12,
      product_name: "Rifter BPC (Copy)",
      activity_id: 3,
      start_date: addHours(now, -20),
      end_date: addHours(now, 4),
      status: "in-progress",
    },
    {
      job_id: 13,
      product_name: "Rifter",
      activity_id: 1,
      start_date: addHours(now, 5),
      end_date: addHours(now, 8),
      status: "in-progress",
    },
  ],
  90000004: [
    {
      job_id: 14,
      product_name: "Oxygen Isotopes",
      activity_id: 6,
      start_date: addHours(now, -1),
      end_date: addHours(now, 6),
      status: "in-progress",
    },
    {
      job_id: 15,
      product_name: "Helium Isotopes",
      activity_id: 6,
      start_date: addHours(now, -1),
      end_date: addHours(now, 6),
      status: "in-progress",
    },
  ],
  90000005: [],
  90000006: [
    {
      job_id: 16,
      product_name: "Megathron",
      activity_id: 1,
      start_date: addHours(now, -48),
      end_date: addHours(now, 24),
      status: "in-progress",
    },
    {
      job_id: 17,
      product_name: "Apocalypse",
      activity_id: 1,
      start_date: addHours(now, -40),
      end_date: addHours(now, 32),
      status: "in-progress",
    },
    {
      job_id: 18,
      product_name: "Raven",
      activity_id: 1,
      start_date: addHours(now, -32),
      end_date: addHours(now, 40),
      status: "in-progress",
    },
    {
      job_id: 19,
      product_name: "Tempest",
      activity_id: 1,
      start_date: addHours(now, -24),
      end_date: addHours(now, 48),
      status: "in-progress",
    },
    {
      job_id: 20,
      product_name: "Scorpion",
      activity_id: 1,
      start_date: addHours(now, -16),
      end_date: addHours(now, 56),
      status: "in-progress",
    },
  ],
  90000007: [
    {
      job_id: 21,
      product_name: "T2 Ammo Crystal (Invention)",
      activity_id: 8,
      start_date: addHours(now, -2),
      end_date: addHours(now, -1),
      status: "completed",
    },
    {
      job_id: 22,
      product_name: "Conflagration S",
      activity_id: 1,
      start_date: addHours(now, 1),
      end_date: addHours(now, 2),
      status: "in-progress",
    },
  ],
  90000008: [],
  90000009: [
    {
      job_id: 23,
      product_name: "1MN Afterburner I",
      activity_id: 1,
      start_date: addHours(now, -0.5),
      end_date: addHours(now, 0.5),
      status: "in-progress",
    },
  ],
  90000010: [],
  90000011: [],
  90000012: [
    {
      job_id: 24,
      product_name: "T2 Blueprint (Copy)",
      activity_id: 3,
      start_date: addHours(now, -2),
      end_date: addHours(now, 3),
      status: "in-progress",
    },
    {
      job_id: 25,
      product_name: "T2 Blueprint (Copy)",
      activity_id: 3,
      start_date: addHours(now, -1),
      end_date: addHours(now, 4),
      status: "in-progress",
    },
  ],
};
