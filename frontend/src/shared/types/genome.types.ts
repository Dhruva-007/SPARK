/**
 * SPARK — Completion Genome Types
 */

export interface GenomeProductivity {
  peakHours: number[];
  averageFocusDuration: number;
  optimalSessionLength: number;
  recoveryTimeNeeded: number;
}

export interface GenomeEstimation {
  averageUnderestimationFactor: number;
  complexityCalibration: {
    low: number;
    medium: number;
    high: number;
  };
}

export interface GenomeProcrastination {
  triggers: string[];
  averageDelayDays: number;
  startingDifficulty: number;
  recoveryPattern: "slow_start" | "sprint" | "consistent";
}

export interface GenomeCompletion {
  successRate: number;
  totalTasksCompleted: number;
  totalTasksFailed: number;
  averageCompletionAccuracy: number;
  bestCompletionDayOfWeek: number;
  streakCurrent: number;
  streakBest: number;
}

export interface GenomePreferences {
  taskOrderPreference: "deadline" | "complexity" | "energy";
  communicationStyle: "direct" | "gentle" | "motivational";
  interventionPreference: "minimal" | "moderate" | "aggressive";
  breakFrequency: number;
}

export interface GenomeInterventionHistory {
  totalInterventions: number;
  successfulInterventions: number;
  mostEffectiveLevel: number;
  leastEffectiveLevel: number;
}

export interface CompletionGenome {
  version: number;
  updatedAt: string;
  productivity: GenomeProductivity;
  estimation: GenomeEstimation;
  procrastination: GenomeProcrastination;
  completion: GenomeCompletion;
  preferences: GenomePreferences;
  interventionHistory: GenomeInterventionHistory;
}

export interface GenomeInsight {
  category: "productivity" | "procrastination" | "estimation" | "completion";
  title: string;
  description: string;
  actionable: string;
  confidence: number;
}