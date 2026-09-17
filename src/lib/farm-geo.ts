// Real property survey (KML-derived) geometry, ported from the original
// prototype dashboard's farm map. The plot shapes and boundary are real;
// only the company name they came from is deliberately not carried over
// anywhere in this app. Cuartel numbers here match the seeded demo plants
// ("Cuartel 1".."Cuartel 14").
export const FARM_GEO = {
  viewBox: "0 0 1308.7 1430.8",
  farmPath:
    "M 203.0,40.0 L 40.0,216.0 L 414.0,565.1 L 377.8,817.9 L 661.7,1226.3 L 904.5,1390.8 L 1268.7,612.1 L 203.0,40.0 Z",
  cuarteles: [
    { id: 1, path: "M 220.9,111.2 L 201.1,117.6 L 183.7,162.7 L 281.0,230.5 L 381.5,195.2 L 367.1,166.1 L 322.8,143.9 L 263.8,122.4 L 220.9,111.2 Z" },
    { id: 2, path: "M 381.2,195.5 L 280.9,230.8 L 281.4,263.1 L 303.6,294.0 L 341.0,316.9 L 363.4,327.1 L 492.1,286.0 L 381.2,195.5 Z" },
    { id: 3, path: "M 491.7,286.1 L 363.3,326.8 L 397.5,369.3 L 428.3,366.1 L 450.2,371.3 L 471.2,385.4 L 498.5,384.8 L 578.9,358.6 L 491.7,286.1 Z" },
    { id: 4, path: "M 494.6,385.4 L 534.3,459.3 L 556.6,500.1 L 607.6,540.8 L 674.3,521.3 L 662.5,479.2 L 661.1,439.1 L 578.8,358.7 L 494.6,385.4 Z" },
    { id: 5, path: "M 808.2,367.5 L 727.7,484.1 L 787.7,550.4 L 885.4,615.1 L 1000.8,640.3 L 1125.7,672.2 L 1227.6,701.4 L 1265.1,619.0 L 808.2,367.5 Z" },
    { id: 6, path: "M 660.9,439.3 L 662.1,478.8 L 674.2,522.6 L 720.5,572.6 L 766.9,626.1 L 793.1,657.2 L 829.6,658.6 L 849.5,653.3 L 885.9,615.6 L 787.7,550.4 L 727.6,484.0 L 660.9,439.3 Z" },
    { id: 7, path: "M 578.3,524.7 L 532.4,560.8 L 605.5,647.3 L 655.2,662.4 L 707.3,726.5 L 758.6,746.9 L 787.6,742.0 L 794.6,698.4 L 792.8,656.5 L 673.2,521.7 L 608.0,541.4 L 578.3,524.7 Z" },
    { id: 8, path: "M 470.9,385.9 L 428.1,401.0 L 408.0,412.1 L 479.9,487.7 L 503.0,508.5 L 554.4,497.9 L 494.0,384.8 L 470.9,385.9 Z" },
    { id: 9, path: "M 150.9,182.3 L 102.2,216.2 L 116.0,244.1 L 182.7,270.3 L 228.6,327.1 L 291.7,384.8 L 364.4,407.4 L 398.0,369.8 L 363.8,327.2 L 340.0,316.8 L 303.5,294.0 L 281.7,263.3 L 280.8,229.7 L 183.6,162.6 L 150.9,182.3 Z" },
    { id: 10, path: "M 466.5,545.3 L 475.4,658.2 L 594.0,711.3 L 718.0,900.4 L 751.0,929.7 L 802.7,981.2 L 787.9,741.5 L 710.3,744.5 L 629.3,661.1 L 570.1,635.6 L 466.5,545.3 Z" },
    { id: 11, path: "M 803.4,981.1 L 1032.0,1119.1 L 1088.2,998.4 L 796.5,868.9 L 803.4,981.1 Z" },
    { id: 12, path: "M 795.8,868.6 L 1088.1,998.3 L 1130.5,906.1 L 789.4,752.3 L 795.8,868.6 Z" },
    { id: 13, path: "M 794.1,697.8 L 786.6,741.3 L 789.6,753.2 L 1130.6,906.4 L 1170.1,824.0 L 794.1,657.4 L 794.1,697.8 Z" },
    { id: 14, path: "M 886.3,615.8 L 849.5,653.4 L 828.1,659.0 L 793.1,657.3 L 1169.9,823.9 L 1227.4,700.7 L 886.3,615.8 Z" },
  ],
};

// Arithmetic mean of a path's vertices - good enough to place a status icon
// roughly centered in an irregular plot, without needing a true polygon
// centroid calculation.
export function pathCentroid(path: string): [number, number] {
  const nums = path.match(/-?\d+(\.\d+)?/g)?.map(Number) ?? [];
  let sx = 0;
  let sy = 0;
  let n = 0;
  for (let i = 0; i + 1 < nums.length; i += 2) {
    sx += nums[i];
    sy += nums[i + 1];
    n++;
  }
  return n ? [sx / n, sy / n] : [0, 0];
}
