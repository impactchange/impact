# backend/services/budget_tracking.py
from typing import Dict, Any, List
from datetime import datetime

def generate_detailed_budget_tracking(project_data: dict, assessment_data: dict, implementation_plan: dict) -> dict:
    """Generate detailed task-level and phase-level budget tracking"""

    # Extract implementation plan weeks for budget analysis
    weeks = implementation_plan.get("weeks", {})

    # Calculate task-level budget breakdown
    task_level_budgets = []
    phase_level_budgets = {}

    for week_num, week_data in weeks.items():
        task_budget = {
            "week": int(week_num),
            "task_id": week_data.get("task_id", f"task_{week_num}"),
            "task_name": week_data.get("title", ""),
            "phase": week_data.get("phase", ""),
            "budgeted_amount": week_data.get("final_budget", 0),
            "spent_amount": 0,  # To be updated as project progresses
            "remaining_amount": week_data.get("final_budget", 0),
            "variance": 0,
            "variance_percentage": 0,
            "risk_level": week_data.get("risk_level", "Medium"),
            "completion_percentage": 0,
            "burn_rate": 0,
            "projected_final_cost": week_data.get("final_budget", 0),
            "cost_performance_index": 1.0,
            "budget_alerts": []
        }
        task_level_budgets.append(task_budget)

        # Aggregate by phase
        phase = week_data.get("phase", "Unknown")
        if phase not in phase_level_budgets:
            phase_level_budgets[phase] = {
                "phase_name": phase,
                "total_budgeted": 0,
                "total_spent": 0,
                "total_remaining": 0,
                "variance": 0,
                "variance_percentage": 0,
                "completion_percentage": 0,
                "risk_level": "Low",
                "tasks_count": 0,
                "on_track_tasks": 0,
                "at_risk_tasks": 0,
                "overrun_tasks": 0
            }

        phase_level_budgets[phase]["total_budgeted"] += week_data.get("final_budget", 0)
        phase_level_budgets[phase]["total_remaining"] += week_data.get("final_budget", 0)
        phase_level_budgets[phase]["tasks_count"] += 1

        if week_data.get("risk_level") == "Low":
            phase_level_budgets[phase]["on_track_tasks"] += 1
        elif week_data.get("risk_level") == "High":
            phase_level_budgets[phase]["at_risk_tasks"] += 1

    # Calculate overall project budget metrics
    total_budgeted = sum(task["budgeted_amount"] for task in task_level_budgets)
    total_spent = sum(task["spent_amount"] for task in task_level_budgets)
    total_remaining = total_budgeted - total_spent

    # Generate budget alerts
    budget_alerts = generate_budget_alerts(task_level_budgets, list(phase_level_budgets.values()), total_budgeted, total_spent)

    # Calculate cost performance metrics
    cost_performance = calculate_cost_performance_metrics(task_level_budgets, total_budgeted, total_spent)

    return {
        "project_id": project_data.get("id", ""),
        "project_name": project_data.get("project_name", ""),
        "budget_tracking": {
            "task_level_budgets": task_level_budgets,
            "phase_level_budgets": list(phase_level_budgets.values()),
            "overall_metrics": {
                "total_budgeted": total_budgeted,
                "total_spent": total_spent,
                "total_remaining": total_remaining,
                "budget_utilization": (total_spent / total_budgeted * 100) if total_budgeted > 0 else 0,
                "projected_final_cost": cost_performance["projected_final_cost"],
                "cost_variance": total_spent - total_budgeted,
                "cost_variance_percentage": ((total_spent - total_budgeted) / total_budgeted * 100) if total_budgeted > 0 else 0,
                "cost_performance_index": cost_performance["cost_performance_index"],
                "budget_health": cost_performance["budget_health"]
            }
        },
        "budget_alerts": budget_alerts,
        "cost_forecasting": cost_performance["forecasting"],
        "generated_at": datetime.utcnow()
    }

def generate_budget_alerts(task_budgets: List[dict], phase_budgets: List[dict], total_budgeted: float, total_spent: float) -> List[dict]:
    """Generate real-time budget alerts based on spending patterns"""
    alerts = []

    # Overall budget alerts
    utilization = (total_spent / total_budgeted * 100) if total_budgeted > 0 else 0

    if utilization > 90:
        alerts.append({
            "type": "Critical",
            "category": "Overall Budget",
            "severity": "High",
            "message": f"Project budget {utilization:.1f}% utilized - immediate action required",
            "recommended_action": "Implement emergency cost controls and review remaining scope",
            "threshold": 90,
            "current_value": utilization
        })
    elif utilization > 75:
        alerts.append({
            "type": "Warning",
            "category": "Overall Budget",
            "severity": "Medium",
            "message": f"Project budget {utilization:.1f}% utilized - monitor closely",
            "recommended_action": "Review upcoming expenses and optimize resource allocation",
            "threshold": 75,
            "current_value": utilization
        })

    # Task-level alerts
    for task in task_budgets:
        if task["risk_level"] == "High" and task["budgeted_amount"] > 5000:  # High-value, high-risk tasks
            alerts.append({
                "type": "Risk",
                "category": "Task Budget",
                "severity": "Medium",
                "message": f"High-risk task '{task['task_name']}' requires attention (${task['budgeted_amount']:,.0f} budget)",
                "recommended_action": "Implement additional oversight and controls for this task",
                "task_id": task["task_id"],
                "budgeted_amount": task["budgeted_amount"]
            })

    # Phase-level alerts
    for phase in phase_budgets:
        if phase["at_risk_tasks"] > phase["on_track_tasks"]:
            alerts.append({
                "type": "Risk",
                "category": "Phase Budget",
                "severity": "Medium",
                "message": f"Phase '{phase['phase_name']}' has more at-risk tasks ({phase['at_risk_tasks']}) than on-track tasks ({phase['on_track_tasks']})",
                "recommended_action": "Focus additional resources on this phase",
                "phase_name": phase["phase_name"],
                "at_risk_tasks": phase["at_risk_tasks"]
            })

    return alerts

def calculate_cost_performance_metrics(task_budgets: List[dict], total_budgeted: float, total_spent: float) -> dict:
    """Calculate advanced cost performance metrics"""

    # Cost Performance Index (CPI)
    earned_value = sum(task["budgeted_amount"] * (task["completion_percentage"] / 100) for task in task_budgets)
    cpi = earned_value / total_spent if total_spent > 0 else 1.0

    # Estimate at Completion (EAC)
    eac = total_budgeted / cpi if cpi > 0 else total_budgeted

    # Variance at Completion (VAC)
    vac = total_budgeted - eac

    # Budget health assessment
    if cpi >= 1.1:
        budget_health = "Excellent"
    elif cpi >= 0.95:
        budget_health = "Good"
    elif cpi >= 0.85:
        budget_health = "Concerning"
    else:
        budget_health = "Critical"

    return {
        "cost_performance_index": round(cpi, 2),
        "projected_final_cost": round(eac, 2),
        "variance_at_completion": round(vac, 2),
        "budget_health": budget_health,
        "forecasting": {
            "estimated_final_cost": round(eac, 2),
            "cost_overrun_risk": max(0, round((eac - total_budgeted) / total_budgeted * 100, 1)) if total_budgeted > 0 else 0,
            "funds_remaining": max(0, round(total_budgeted - eac, 2)),
            "performance_trend": "Above Budget" if cpi < 0.95 else "On Budget" if cpi < 1.05 else "Under Budget"
        }
    }