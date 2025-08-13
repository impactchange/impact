ASSESSMENT_TYPES = {
    "general_readiness": {
        "dimensions": [
            {"id": "change_management_maturity", "name": "Change Management Maturity"},
            {"id": "communication_effectiveness", "name": "Communication Effectiveness"},
            {"id": "leadership_support", "name": "Leadership Support"},
            {"id": "workforce_adaptability", "name": "Workforce Adaptability"},
            {"id": "resource_adequacy", "name": "Resource Adequacy"}
        ]
    },
    "software_implementation": {
        "dimensions": [
            {"id": "change_management_maturity", "name": "Change Management Maturity"},
            {"id": "communication_effectiveness", "name": "Communication Effectiveness"},
            {"id": "leadership_support", "name": "Leadership Support"},
            {"id": "workforce_adaptability", "name": "Workforce Adaptability"},
            {"id": "resource_adequacy", "name": "Resource Adequacy"}
        ]
    }
}

# backend/data/constants.py

ASSESSMENT_TYPES = {
    "general_readiness": {
        "name": "General Change Readiness Assessment",
        "description": "Comprehensive organizational change readiness evaluation for any type of transformation project",
        "icon": "📋",
        "dimensions": [
            {
                "id": "leadership_commitment",
                "name": "Leadership Commitment & Sponsorship",
                "description": "How committed is senior leadership to this change initiative?",
                "category": "core"
            },
            {
                "id": "organizational_culture",
                "name": "Organizational Culture & Change History",
                "description": "How well does the organization typically adapt to change?",
                "category": "core"
            },
            {
                "id": "resource_availability",
                "name": "Resource Availability & Capability",
                "description": "Are adequate financial, human, and technical resources available?",
                "category": "core"
            },
            {
                "id": "stakeholder_engagement",
                "name": "Stakeholder Engagement & Communication",
                "description": "How effective are existing stakeholder engagement capabilities?",
                "category": "core"
            },
            {
                "id": "training_capability",
                "name": "Training & Development Capability",
                "description": "What training capabilities and infrastructure exist?",
                "category": "core"
            }
        ]
    },
    "software_implementation": {
        "name": "Software Implementation Readiness Assessment",
        "description": "Specialized assessment for software implementation projects and technology adoption",
        "icon": "💻",
        "dimensions": [
            {
                "id": "leadership_commitment",
                "name": "Leadership Commitment & Sponsorship",
                "description": "How committed is senior leadership to this software implementation?",
                "category": "core"
            },
            {
                "id": "organizational_culture",
                "name": "Organizational Culture & Change History",
                "description": "How well does the organization adapt to new technology?",
                "category": "core"
            },
            {
                "id": "resource_availability",
                "name": "Resource Availability & Capability",
                "description": "Are adequate resources available for software implementation?",
                "category": "core"
            },
            {
                "id": "stakeholder_engagement",
                "name": "Stakeholder Engagement & Communication",
                "description": "How effective are communication channels for technology changes?",
                "category": "core"
            },
            {
                "id": "training_capability",
                "name": "Training & Development Capability",
                "description": "What technical training capabilities exist?",
                "category": "core"
            },
            {
                "id": "technical_infrastructure",
                "name": "Technical Infrastructure Readiness",
                "description": "How ready is the technical infrastructure for new software?",
                "category": "specialized"
            },
            {
                "id": "user_adoption_readiness",
                "name": "User Adoption Readiness",
                "description": "How ready are end users to adopt new software systems?",
                "category": "specialized"
            },
            {
                "id": "data_migration_readiness",
                "name": "Data Migration & Integration Readiness",
                "description": "How prepared is the organization for data migration and system integration?",
                "category": "specialized"
            }
        ]
    },
    "business_process": {
        "name": "Business Process Evaluation Assessment",
        "description": "Assessment for business process improvement and operational transformation projects",
        "icon": "⚙️",
        "dimensions": [
            {
                "id": "leadership_commitment",
                "name": "Leadership Commitment & Sponsorship",
                "description": "How committed is leadership to business process improvement?",
                "category": "core"
            },
            {
                "id": "organizational_culture",
                "name": "Organizational Culture & Change History",
                "description": "How well does the organization adapt to process changes?",
                "category": "core"
            },
            {
                "id": "resource_availability",
                "name": "Resource Availability & Capability",
                "description": "Are adequate resources available for process transformation?",
                "category": "core"
            },
            {
                "id": "stakeholder_engagement",
                "name": "Stakeholder Engagement & Communication",
                "description": "How effective are stakeholder engagement strategies?",
                "category": "core"
            },
            {
                "id": "training_capability",
                "name": "Training & Development Capability",
                "description": "What process training capabilities exist?",
                "category": "core"
            },
            {
                "id": "process_maturity",
                "name": "Current Process Maturity",
                "description": "How mature and documented are current business processes?",
                "category": "specialized"
            },
            {
                "id": "cross_functional_collaboration",
                "name": "Cross-Functional Collaboration",
                "description": "How effectively do departments collaborate on process improvements?",
                "category": "specialized"
            },
            {
                "id": "performance_measurement",
                "name": "Performance Measurement Capability",
                "description": "How well can the organization measure and track process performance?",
                "category": "specialized"
            }
        ]
    },
    "manufacturing_operations": {
        "name": "Manufacturing Operations Assessment",
        "description": "Assessment for manufacturing line evaluations and operational improvements",
        "icon": "🏭",
        "dimensions": [
            {
                "id": "leadership_commitment",
                "name": "Leadership Commitment & Sponsorship",
                "description": "How committed is leadership to operational improvements?",
                "category": "core"
            },
            {
                "id": "organizational_culture",
                "name": "Organizational Culture & Change History",
                "description": "How well does the organization adapt to operational changes?",
                "category": "core"
            },
            {
                "id": "resource_availability",
                "name": "Resource Availability & Capability",
                "description": "Are adequate resources available for operational transformation?",
                "category": "core"
            },
            {
                "id": "stakeholder_engagement",
                "name": "Stakeholder Engagement & Communication",
                "description": "How effective are communication channels in the manufacturing environment?",
                "category": "core"
            },
            {
                "id": "training_capability",
                "name": "Training & Development Capability",
                "description": "What operational training capabilities exist?",
                "category": "core"
            },
            {
                "id": "operational_constraints",
                "name": "Operational Constraints Management",
                "description": "How manageable are operational constraints during improvements?",
                "category": "specialized"
            },
            {
                "id": "maintenance_operations_alignment",
                "name": "Maintenance-Operations Alignment",
                "description": "How well aligned are maintenance and operations teams?",
                "category": "specialized"
            },
            {
                "id": "shift_coordination",
                "name": "Shift Work & Coordination",
                "description": "How well can shift patterns accommodate improvement activities?",
                "category": "specialized"
            },
            {
                "id": "safety_compliance",
                "name": "Safety & Compliance Integration",
                "description": "How well can safety and regulatory requirements be integrated?",
                "category": "specialized"
            }
        ]
    }
}

IMPACT_PHASES = {
    "investigate": {
        "name": "Investigate & Assess",
        "description": "Understanding current state and establishing transformation foundation",
        "order": 1,
        "newton_law": "First Law - Overcoming Organizational Inertia",
        "newton_insight": "Organizations at rest tend to stay at rest. Significant force is required to overcome initial inertia and establish change momentum.",
        "objectives": [
            "Comprehensively evaluate current state and organizational readiness",
            "Assess stakeholder landscape and change capacity",
            "Identify risks, opportunities, and critical success factors",
            "Establish baseline measurements and performance metrics",
            "Map cultural factors and organizational dynamics"
        ],
        "key_activities": [
            "Conduct comprehensive stakeholder analysis",
            "Execute multi-dimensional change readiness assessment",
            "Perform current state analysis and gap identification",
            "Assess organizational culture and change history",
            "Identify risks and develop mitigation strategies",
            "Map informal networks and influence patterns",
            "Evaluate technical and operational capabilities"
        ],
        "deliverables": [
            {"name": "Stakeholder Analysis Report", "type": "analysis", "required": True},
            {"name": "Change Readiness Assessment", "type": "assessment", "required": True},
            {"name": "Current State Analysis", "type": "baseline", "required": True},
            {"name": "Risk Assessment Matrix", "type": "assessment", "required": True},
            {"name": "Cultural Assessment Report", "type": "analysis", "required": True},
            {"name": "Technical Readiness Evaluation", "type": "assessment", "required": False}
        ],
        "tools": [
            "Stakeholder Analysis Template",
            "Change Readiness Assessment Survey",
            "Risk Assessment Matrix",
            "Cultural Assessment Framework",
            "Current State Analysis Tool"
        ],
        "completion_criteria": [
            "All stakeholders identified and analyzed",
            "Change readiness score of 3.5+ achieved or improvement plan established",
            "Current state baseline documented with improvement opportunities",
            "Critical risks identified with mitigation strategies",
            "Cultural factors mapped with engagement strategies"
        ],
        "universal_focus": "Understand the current organizational state and identify the specific factors that will impact transformation success for any type of change initiative."
    },
    "mobilize": {
        "name": "Mobilize & Prepare",
        "description": "Building infrastructure and preparing for transformation success",
        "order": 2,
        "newton_law": "Second Law - Measuring Forces and Preparing for Acceleration",
        "newton_insight": "Acceleration equals force applied divided by organizational mass. Prepare the right resources and remove resistance to calculate required force accurately.",
        "objectives": [
            "Develop comprehensive change management strategy",
            "Establish governance structures and communication frameworks",
            "Create training and development programs for all stakeholders",
            "Build change champion networks across the organization",
            "Prepare measurement systems and success criteria"
        ],
        "key_activities": [
            "Develop detailed change management plan and strategy",
            "Create multi-channel communication strategy and materials",
            "Design role-based training programs for diverse audiences",
            "Establish change champion network covering all areas",
            "Develop success metrics and measurement frameworks",
            "Create resource allocation plans and timelines",
            "Establish issue escalation and support procedures"
        ],
        "deliverables": [
            {"name": "Change Management Plan", "type": "plan", "required": True},
            {"name": "Communication Strategy and Plan", "type": "plan", "required": True},
            {"name": "Training Program Design", "type": "plan", "required": True},
            {"name": "Change Champion Network Plan", "type": "plan", "required": True},
            {"name": "Success Metrics Framework", "type": "framework", "required": True},
            {"name": "Resource Allocation Plan", "type": "plan", "required": False}
        ],
        "tools": [
            "Change Management Plan Template",
            "Communication Plan Template",
            "Training Strategy Framework",
            "Champion Network Development Guide",
            "Success Metrics Template"
        ],
        "completion_criteria": [
            "Comprehensive change plan approved by leadership",
            "Champion network established covering all key areas",
            "Communication strategy tested and validated with audiences",
            "Training materials developed and tested for effectiveness",
            "Success metrics defined and measurement systems prepared"
        ],
        "universal_focus": "Ensure all stakeholders understand the transformation objectives and benefits, and are prepared to support the change initiative with appropriate resources and capabilities."
    },
    "pilot": {
        "name": "Pilot & Adapt",
        "description": "Testing approach with limited group and refining strategies",
        "order": 3,
        "newton_law": "Third Law - Testing Action-Reaction in Controlled Environment",
        "newton_insight": "For every action, there is an equal and opposite reaction. Test with pilot group to measure and understand resistance patterns before full deployment.",
        "objectives": [
            "Validate change strategies in real manufacturing environment",
            "Test maintenance-operations integration in controlled setting",
            "Identify and resolve issues before full-scale deployment",
            "Build confidence through demonstrated maintenance excellence results",
            "Refine approaches based on manufacturing-specific feedback"
        ],
        "key_activities": [
            "Select representative pilot group from maintenance and operations",
            "Execute pilot implementation with intensive support",
            "Monitor pilot performance and gather comprehensive feedback",
            "Demonstrate connection between maintenance improvements and operational results",
            "Capture lessons learned and refine strategies",
            "Develop success stories proving maintenance-manufacturing excellence connection",
            "Prepare scaling plan based on pilot learnings"
        ],
        "deliverables": [
            {"name": "Pilot Implementation Plan", "type": "plan", "required": True},
            {"name": "Pilot Results Analysis", "type": "analysis", "required": True},
            {"name": "Lessons Learned Report", "type": "report", "required": True},
            {"name": "Success Stories Documentation", "type": "documentation", "required": True},
            {"name": "Refined Implementation Strategy", "type": "strategy", "required": True},
            {"name": "Scaling Preparation Plan", "type": "plan", "required": False}
        ],
        "tools": [
            "Pilot Implementation Guide",
            "Pilot Feedback Collection Tools",
            "Performance Measurement Dashboard",
            "Success Story Template",
            "Strategy Refinement Framework"
        ],
        "completion_criteria": [
            "Pilot success metrics achieved demonstrating maintenance-operations benefits",
            "Key learnings captured and strategies refined",
            "Pilot participants serve as advocates for full deployment",
            "Success stories document clear maintenance-manufacturing performance connection",
            "Scaling plan validated and approved"
        ],
        "manufacturing_focus": "Prove that maintenance improvements directly drive operational benefits in your specific manufacturing environment."
    },
    "activate": {
        "name": "Activate & Deploy",
        "description": "Full-scale implementation with comprehensive support",
        "order": 4,
        "newton_law": "Applied Force - Implementation in Motion",
        "newton_insight": "Apply consistent force to maintain momentum and overcome organizational inertia during full manufacturing implementation.",
        "objectives": [
            "Execute full-scale deployment across entire manufacturing organization",
            "Maintain momentum while managing resistance effectively",
            "Ensure maintenance excellence becomes embedded in operations",
            "Track performance improvements and demonstrate manufacturing impact",
            "Provide intensive support during transition period"
        ],
        "key_activities": [
            "Launch full deployment with manufacturing-appropriate sequencing",
            "Execute comprehensive training across all shifts and departments",
            "Monitor adoption rates and performance metrics continuously",
            "Manage resistance with manufacturing-specific strategies",
            "Support maintenance and operations teams through transition",
            "Collect and communicate success stories regularly",
            "Maintain focus on maintenance-manufacturing excellence connection"
        ],
        "deliverables": [
            {"name": "Deployment Execution Plan", "type": "plan", "required": True},
            {"name": "Training Delivery Records", "type": "records", "required": True},
            {"name": "Performance Monitoring Reports", "type": "reports", "required": True},
            {"name": "Resistance Management Log", "type": "log", "required": True},
            {"name": "Success Communication Materials", "type": "materials", "required": True},
            {"name": "Manufacturing Impact Analysis", "type": "analysis", "required": False}
        ],
        "tools": [
            "Deployment Management Dashboard",
            "Resistance Management Toolkit",
            "Performance Tracking System",
            "Communication Campaign Tools",
            "Manufacturing Metrics Monitor"
        ],
        "completion_criteria": [
            "90%+ user adoption achieved across maintenance and operations",
            "Manufacturing performance improvements documented and validated",
            "Resistance successfully managed with minimal operational disruption",
            "Training completion rates above 95% across all shifts",
            "Maintenance-operations collaboration demonstrably improved"
        ],
        "manufacturing_focus": "Ensure that maintenance excellence becomes embedded throughout the organization and drives measurable manufacturing performance improvements."
    },
    "cement": {
        "name": "Cement & Transfer",
        "description": "Institutionalizing change and transferring ownership",
        "order": 5,
        "newton_law": "Continuous Force Application for Sustainable Motion",
        "newton_insight": "Continuous force application prevents the organization from returning to its original state due to natural inertia.",
        "objectives": [
            "Institutionalize maintenance excellence as part of organizational culture",
            "Transfer ownership from implementation team to operational management",
            "Embed new practices in organizational systems and processes",
            "Establish sustainable maintenance-operations collaboration",
            "Create self-reinforcing systems for continuous improvement"
        ],
        "key_activities": [
            "Document and standardize new maintenance excellence practices",
            "Transfer knowledge and ownership to internal teams",
            "Integrate new practices into performance management systems",
            "Establish ongoing governance and oversight structures",
            "Create sustainability plans for maintenance excellence culture",
            "Implement internal capability development programs",
            "Establish mechanisms for continuous improvement"
        ],
        "deliverables": [
            {"name": "Process Documentation and Standards", "type": "documentation", "required": True},
            {"name": "Knowledge Transfer Plan", "type": "plan", "required": True},
            {"name": "Sustainability Framework", "type": "framework", "required": True},
            {"name": "Internal Capability Development Plan", "type": "plan", "required": True},
            {"name": "Governance Structure Documentation", "type": "documentation", "required": True},
            {"name": "Continuous Improvement Procedures", "type": "procedures", "required": False}
        ],
        "tools": [
            "Process Documentation Templates",
            "Knowledge Transfer Checklist",
            "Sustainability Planning Guide",
            "Governance Framework Template",
            "Continuous Improvement Toolkit"
        ],
        "completion_criteria": [
            "New practices fully documented and embedded in organizational systems",
            "Internal teams capable of sustaining maintenance excellence independently",
            "Performance management systems reflect maintenance-manufacturing connection",
            "Governance structures functioning effectively",
            "Continuous improvement culture established and functioning"
        ],
        "manufacturing_focus": "Ensure that the connection between maintenance excellence and operational performance becomes part of your organizational culture."
    },
    "track": {
        "name": "Track & Optimize",
        "description": "Long-term monitoring and continuous improvement",
        "order": 6,
        "newton_law": "New Equilibrium State with Continuous Optimization",
        "newton_insight": "The organization has reached a new equilibrium state with maintenance excellence integrated and sustainable, enabling continuous optimization.",
        "objectives": [
            "Monitor long-term performance and sustain improvements",
            "Validate implementation guarantee commitments",
            "Identify opportunities for additional manufacturing performance gains",
            "Share best practices and lessons learned",
            "Plan for future manufacturing excellence initiatives"
        ],
        "key_activities": [
            "Monitor KPIs and manufacturing performance metrics continuously",
            "Conduct regular assessment of maintenance excellence sustainability",
            "Identify and implement additional improvement opportunities",
            "Validate guarantee commitments and document achievement",
            "Share success stories and best practices across organization",
            "Plan for advanced maintenance excellence capabilities",
            "Establish long-term strategic planning for manufacturing excellence"
        ],
        "deliverables": [
            {"name": "Performance Monitoring Dashboard", "type": "dashboard", "required": True},
            {"name": "Guarantee Validation Report", "type": "report", "required": True},
            {"name": "Optimization Opportunities Analysis", "type": "analysis", "required": True},
            {"name": "Best Practices Documentation", "type": "documentation", "required": True},
            {"name": "Strategic Planning Report", "type": "report", "required": True},
            {"name": "ROI and Benefits Realization Report", "type": "report", "required": False}
        ],
        "tools": [
            "Performance Dashboard System",
            "Guarantee Validation Framework",
            "Optimization Analysis Tools",
            "Best Practice Capture Templates",
            "Strategic Planning Framework"
        ],
        "completion_criteria": [
            "All guarantee commitments met and validated",
            "Manufacturing performance improvements sustained over 12+ months",
            "Continuous improvement processes functioning effectively",
            "Organization recognized as maintenance excellence leader",
            "Strategic plan developed for future manufacturing excellence initiatives"
        ],
        "manufacturing_focus": "Demonstrate that maintenance excellence continues to drive manufacturing performance improvements and creates sustainable competitive advantage."
    }
}