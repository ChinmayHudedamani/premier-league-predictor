export function factorial(n: number): number {
  if (n <= 1) return 1;
  let res = 1;
  for (let i = 2; i <= n; i++) res *= i;
  return res;
}

export function poissonPMF(k: number, lambda: number): number {
  return (Math.pow(lambda, k) * Math.exp(-lambda)) / factorial(k);
}

export interface PoissonSimulationResult {
  pctHome: string;
  pctDraw: string;
  pctAway: string;
  likelyHomeG: number;
  likelyAwayG: number;
}

export function runPoissonSimulation(lambdaHome: number, lambdaAway: number): PoissonSimulationResult {
  const maxGoals = 7;
  const homeProbs: number[] = [];
  const awayProbs: number[] = [];

  for (let g = 0; g < maxGoals; g++) {
    homeProbs[g] = poissonPMF(g, lambdaHome);
    awayProbs[g] = poissonPMF(g, lambdaAway);
  }

  let pHomeWin = 0;
  let pDraw = 0;
  let pAwayWin = 0;
  let maxProb = -1;
  let likelyHomeG = 0;
  let likelyAwayG = 0;

  for (let h = 0; h < maxGoals; h++) {
    for (let a = 0; a < maxGoals; a++) {
      const p = homeProbs[h] * awayProbs[a];
      if (h > a) pHomeWin += p;
      else if (h === a) pDraw += p;
      else pAwayWin += p;

      if (p > maxProb) {
        maxProb = p;
        likelyHomeG = h;
        likelyAwayG = a;
      }
    }
  }

  const sumP = pHomeWin + pDraw + pAwayWin;
  return {
    pctHome: ((pHomeWin / sumP) * 100).toFixed(1),
    pctDraw: ((pDraw / sumP) * 100).toFixed(1),
    pctAway: ((pAwayWin / sumP) * 100).toFixed(1),
    likelyHomeG,
    likelyAwayG,
  };
}
