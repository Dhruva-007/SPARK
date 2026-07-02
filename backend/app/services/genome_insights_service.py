"""
SPARK — Genome Insights Service
Generates AI-powered behavioral insights from the Completion Genome.

Insights are organized into categories:
- Productivity: peak hours, focus patterns, energy management
- Estimation: accuracy trends, complexity calibration
- Procrastination: triggers, delay patterns, recovery strategies
- Completion: success rate trends, streak analysis
- Intervention: what levels of support work best

Each insight is:
- Actionable (tells the user what to do differently)
- Specific (references real data from their genome)
- Time-relevant (considers current time of day)
"""

from datetime import datetime, timezone
from typing import Optional

from app.core.logging import get_logger
from app.models.genome import CompletionGenome
from app.services.genome_service import GenomeService

logger = get_logger(__name__)


class GenomeInsightsService:
    """Generates actionable insights from the Completion Genome."""

    def __init__(self) -> None:
        self._genome_service = GenomeService()

    def get_full_insights(self, user_id: str) -> dict:
        """
        Returns the complete genome insights package for the frontend.
        Includes all categories and the formatted genome profile.
        """
        genome = self._genome_service.get_genome(user_id)
        now = datetime.now(timezone.utc)
        current_hour = now.hour

        return {
            "profile": self._build_profile(genome, current_hour),
            "insights": self._generate_insights(genome, current_hour),
            "productivity_data": self._build_productivity_data(genome, current_hour),
            "estimation_data": self._build_estimation_data(genome),
            "completion_data": self._build_completion_data(genome),
            "intervention_data": self._build_intervention_data(genome),
            "generated_at": now.isoformat(),
        }

    def get_ai_insights(self, user_id: str) -> list[dict]:
        """
        Generates AI-powered insights using Gemini.
        Falls back to rule-based insights if AI is unavailable.
        """
        genome = self._genome_service.get_genome(user_id)
        current_hour = datetime.now(timezone.utc).hour

        try:
            return self._generate_ai_insights(genome, current_hour)
        except Exception as exc:
            logger.warning(
                "AI insight generation failed — using rule-based",
                error=str(exc),
            )
            return self._generate_insights(genome, current_hour)

    def _build_profile(self, genome: CompletionGenome, current_hour: int) -> dict:
        """Builds a structured genome profile for the frontend."""
        peak_hours = genome.productivity.peakHours
        is_peak = current_hour in peak_hours

        # Calculate genome maturity (how much data we have)
        total_tasks = (
            genome.completion.totalTasksCompleted +
            genome.completion.totalTasksFailed
        )
        if total_tasks == 0:
            maturity = "initializing"
            maturity_level = 0
        elif total_tasks < 5:
            maturity = "learning"
            maturity_level = 1
        elif total_tasks < 15:
            maturity = "developing"
            maturity_level = 2
        elif total_tasks < 30:
            maturity = "calibrated"
            maturity_level = 3
        else:
            maturity = "expert"
            maturity_level = 4

        # Overall health score from genome data
        health_factors = [
            genome.completion.successRate * 100,
            max(0, 100 - genome.procrastination.startingDifficulty * 10),
            min(100, (1 / max(genome.estimation.averageUnderestimationFactor, 0.5)) * 100),
            genome.completion.streakCurrent * 10,
        ]
        health_score = min(100, sum(health_factors) / len(health_factors))

        return {
            "health_score": round(health_score, 1),
            "maturity": maturity,
            "maturity_level": maturity_level,
            "total_tasks_analyzed": total_tasks,
            "is_peak_hour": is_peak,
            "current_hour": current_hour,
            "peak_hours": peak_hours,
            "success_rate": round(genome.completion.successRate * 100, 1),
            "streak_current": genome.completion.streakCurrent,
            "streak_best": genome.completion.streakBest,
            "focus_duration": genome.productivity.averageFocusDuration,
            "recovery_pattern": genome.procrastination.recoveryPattern,
            "communication_style": genome.preferences.communicationStyle,
            "version": genome.version,
        }

    def _generate_insights(
        self,
        genome: CompletionGenome,
        current_hour: int,
    ) -> list[dict]:
        """
        Generates rule-based behavioral insights.
        Each insight has: category, title, description, actionable, priority.
        """
        insights: list[dict] = []
        peak_hours = genome.productivity.peakHours

        # ── Productivity insights ────────────────────────────
        is_peak = current_hour in peak_hours
        if is_peak:
            insights.append({
                "category": "productivity",
                "title": "You're in your peak zone",
                "description": (
                    f"Hour {current_hour}:00 is one of your peak productivity hours. "
                    f"Your focus typically lasts {genome.productivity.averageFocusDuration} minutes."
                ),
                "actionable": "Start your most challenging task now for best results.",
                "priority": "high",
            })
        elif peak_hours:
            next_peak = min(
                (h for h in peak_hours if h > current_hour),
                default=peak_hours[0],
            )
            insights.append({
                "category": "productivity",
                "title": "Save deep work for peak hours",
                "description": (
                    f"Your next peak window starts at {next_peak}:00. "
                    f"Current time ({current_hour}:00) is better for lighter tasks."
                ),
                "actionable": f"Handle admin tasks now. Start deep work at {next_peak}:00.",
                "priority": "medium",
            })

        # Focus duration insight
        focus = genome.productivity.averageFocusDuration
        if focus < 30:
            insights.append({
                "category": "productivity",
                "title": "Short focus sessions detected",
                "description": (
                    f"Your average focus duration is {focus} minutes. "
                    f"This is below the 25-minute Pomodoro minimum."
                ),
                "actionable": "Try phone-free 25-minute sessions to build focus stamina.",
                "priority": "high",
            })

        # ── Estimation insights ──────────────────────────────
        underest = genome.estimation.averageUnderestimationFactor
        if underest > 1.4:
            insights.append({
                "category": "estimation",
                "title": f"You underestimate by {(underest - 1) * 100:.0f}%",
                "description": (
                    f"Tasks typically take {underest:.1f}x longer than your estimates. "
                    f"SPARK adjusts deadlines automatically using this factor."
                ),
                "actionable": f"Multiply your time estimates by {underest:.1f}x for accuracy.",
                "priority": "high",
            })
        elif underest < 0.9:
            insights.append({
                "category": "estimation",
                "title": "You overestimate task duration",
                "description": (
                    f"Tasks typically take only {underest:.0%} of your estimated time. "
                    f"You're faster than you think!"
                ),
                "actionable": "Trust your ability — take on more challenging work.",
                "priority": "low",
            })

        # Complexity-specific calibration
        calib = genome.estimation.complexityCalibration
        worst_complexity = max(calib, key=calib.get)
        if calib[worst_complexity] > 1.5:
            insights.append({
                "category": "estimation",
                "title": f"Struggle with {worst_complexity} complexity tasks",
                "description": (
                    f"{worst_complexity.capitalize()} tasks take "
                    f"{calib[worst_complexity]:.1f}x your estimate on average."
                ),
                "actionable": (
                    f"Break {worst_complexity} tasks into smaller sub-tasks "
                    f"before estimating."
                ),
                "priority": "medium",
            })

        # ── Procrastination insights ─────────────────────────
        triggers = genome.procrastination.triggers
        if triggers:
            insights.append({
                "category": "procrastination",
                "title": f"Known procrastination triggers",
                "description": (
                    f"You tend to delay when facing: {', '.join(triggers[:3])}."
                ),
                "actionable": "When you notice these triggers, start with a 5-minute micro-action.",
                "priority": "medium",
            })

        delay = genome.procrastination.averageDelayDays
        if delay > 2:
            insights.append({
                "category": "procrastination",
                "title": f"Average {delay:.1f}-day delay before starting",
                "description": (
                    "You typically wait before starting new tasks. "
                    "SPARK's Activation Agent counters this by starting work for you."
                ),
                "actionable": "Open the task document within 30 minutes of creation.",
                "priority": "high",
            })

        # ── Completion insights ──────────────────────────────
        rate = genome.completion.successRate
        if rate > 0.85:
            insights.append({
                "category": "completion",
                "title": f"Strong completion rate: {rate:.0%}",
                "description": "You consistently finish what you start. Keep it up!",
                "actionable": "Consider taking on more ambitious projects.",
                "priority": "low",
            })
        elif rate < 0.5 and genome.completion.totalTasksCompleted > 3:
            insights.append({
                "category": "completion",
                "title": f"Completion rate needs improvement: {rate:.0%}",
                "description": (
                    "More than half your tasks are not completed on time. "
                    "This may indicate overcommitment."
                ),
                "actionable": "Reduce active tasks to 3-4 at a time. Quality over quantity.",
                "priority": "high",
            })

        streak = genome.completion.streakCurrent
        if streak >= 3:
            insights.append({
                "category": "completion",
                "title": f"🔥 {streak}-task completion streak!",
                "description": f"Your best streak is {genome.completion.streakBest}. Keep pushing!",
                "actionable": "Complete one more task today to extend the streak.",
                "priority": "medium",
            })

        # ── Intervention insights ────────────────────────────
        best_level = genome.interventionHistory.mostEffectiveLevel
        worst_level = genome.interventionHistory.leastEffectiveLevel
        total_interventions = genome.interventionHistory.totalInterventions

        if total_interventions >= 3:
            insights.append({
                "category": "intervention",
                "title": f"Level {best_level} interventions work best for you",
                "description": (
                    f"Out of {total_interventions} interventions, "
                    f"Level {best_level} has the best response rate. "
                    f"Level {worst_level} is least effective."
                ),
                "actionable": f"SPARK will prioritize Level {best_level} interventions.",
                "priority": "low",
            })

        return insights

    def _generate_ai_insights(
        self,
        genome: CompletionGenome,
        current_hour: int,
    ) -> list[dict]:
        """
        Future: Uses Gemini to generate deeper behavioral insights.
        For now, uses rule-based insights.
        Phase 17 will add full AI analysis here.
        """
        return self._generate_insights(genome, current_hour)

    def _build_productivity_data(
        self,
        genome: CompletionGenome,
        current_hour: int,
    ) -> dict:
        """Formats productivity data for the frontend heatmap."""
        peak_hours = genome.productivity.peakHours

        # Build hour-by-hour productivity estimate (0-100)
        hourly_productivity: list[dict] = []
        for hour in range(24):
            if hour in peak_hours:
                score = 85 + (5 if hour == peak_hours[len(peak_hours) // 2] else 0)
            elif any(abs(hour - p) <= 1 for p in peak_hours):
                score = 60
            elif 6 <= hour <= 22:
                score = 35
            else:
                score = 10

            hourly_productivity.append({
                "hour": hour,
                "label": f"{hour:02d}:00",
                "score": score,
                "is_peak": hour in peak_hours,
                "is_current": hour == current_hour,
            })

        return {
            "hourly_productivity": hourly_productivity,
            "peak_hours": peak_hours,
            "focus_duration": genome.productivity.averageFocusDuration,
            "optimal_session": genome.productivity.optimalSessionLength,
            "recovery_needed": genome.productivity.recoveryTimeNeeded,
        }

    def _build_estimation_data(self, genome: CompletionGenome) -> dict:
        """Formats estimation accuracy data for the frontend."""
        calib = genome.estimation.complexityCalibration
        return {
            "underestimation_factor": genome.estimation.averageUnderestimationFactor,
            "accuracy_percentage": round(
                min(100, (1 / max(genome.estimation.averageUnderestimationFactor, 0.1)) * 100),
                1,
            ),
            "complexity_calibration": {
                "low": {"factor": calib.get("low", 1.0), "label": "Low"},
                "medium": {"factor": calib.get("medium", 1.0), "label": "Medium"},
                "high": {"factor": calib.get("high", 1.0), "label": "High"},
            },
        }

    def _build_completion_data(self, genome: CompletionGenome) -> dict:
        """Formats completion statistics for the frontend."""
        return {
            "success_rate": round(genome.completion.successRate * 100, 1),
            "total_completed": genome.completion.totalTasksCompleted,
            "total_failed": genome.completion.totalTasksFailed,
            "completion_accuracy": round(
                genome.completion.averageCompletionAccuracy * 100, 1
            ),
            "best_day": genome.completion.bestCompletionDayOfWeek,
            "streak_current": genome.completion.streakCurrent,
            "streak_best": genome.completion.streakBest,
        }

    def _build_intervention_data(self, genome: CompletionGenome) -> dict:
        """Formats intervention effectiveness data for the frontend."""
        history = genome.interventionHistory
        effectiveness_rate = (
            history.successfulInterventions / max(history.totalInterventions, 1)
        )

        return {
            "total_interventions": history.totalInterventions,
            "successful_interventions": history.successfulInterventions,
            "effectiveness_rate": round(effectiveness_rate * 100, 1),
            "most_effective_level": history.mostEffectiveLevel,
            "least_effective_level": history.leastEffectiveLevel,
        }