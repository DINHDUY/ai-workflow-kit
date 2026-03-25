# workflow.py
"""
Assembles the MAF orchestration workflow for the Next.js pipeline.
Converts Google Stitch UI sketches into production-ready Next.js 15+ applications
using a team of 8 specialized agents coordinated by a MagenticBuilder workflow.

Agents:
- nextjs.orchestrator (manager) - Coordinates the 7-phase pipeline
- nextjs.design-processor - Extracts design tokens from Stitch exports
- nextjs.project-scaffolder - Initializes Next.js 15+ project structure
- nextjs.component-builder - Builds shadcn/ui components
- nextjs.page-assembler - Assembles pages with Server Components
- nextjs.data-layer-integrator - Sets up TanStack Query, forms, auth
- nextjs.quality-polish - Adds accessibility, i18n, performance
- nextjs.test-deployer - Creates tests and deployment config
"""
from pathlib import Path
from agent_framework.orchestrations import MagenticBuilder
from maf.client import client
from maf.agents import create_ms_agent
from maf.parser import build_registry


def build_manager_agent(global_instructions: str | None = None):
    """
    Create the orchestrator agent that coordinates the Next.js pipeline.
    
    This agent manages the 7-phase workflow:
    1. Design Processing (extract tokens from Stitch)
    2. Project Scaffolding (initialize Next.js 15+)
    3. Component Building (shadcn/ui components)
    4. Page Assembly (Server Components + routing)
    5. Data Layer Integration (TanStack Query, forms, auth)
    6. Quality Polish (accessibility, i18n, performance)
    7. Testing & Deployment (Vitest, Playwright, CI/CD)
    """
    base_instructions = (
        "You are the pipeline orchestrator for the Stitch-to-production Next.js workflow. "
        "You coordinate 7 specialized agents that transform Google Stitch UI sketches into "
        "production-ready Next.js 15+ applications.\n\n"
        
        "## Your Responsibilities\n\n"
        
        "1. **Validate inputs** - Ensure Stitch export, project name, and requirements are complete\n"
        "2. **Execute phases sequentially** - Each phase builds on the previous:\n"
        "   - Phase 1: design-processor (extract design tokens)\n"
        "   - Phase 2: project-scaffolder (initialize Next.js project)\n"
        "   - Phase 3: component-builder (build shadcn/ui components)\n"
        "   - Phase 4: page-assembler (assemble pages)\n"
        "   - Phase 5: data-layer-integrator (add TanStack Query, forms, auth)\n"
        "   - Phase 6: quality-polish (accessibility, i18n, performance)\n"
        "   - Phase 7: test-deployer (tests and deployment)\n"
        "3. **Verify handoff documents** - Each phase produces a HANDOFF_*.md consumed by the next\n"
        "4. **Update status** - Maintain ORCHESTRATION_LOG.md with phase completion status\n"
        "5. **Synthesize results** - Provide clear progress updates to the user\n\n"
        
        "## Delegation Strategy\n\n"
        
        "- Delegate to exactly ONE agent per phase\n"
        "- Wait for phase completion before proceeding to next phase\n"
        "- Verify required outputs exist before continuing\n"
        "- If a phase fails, diagnose and retry with corrections\n"
        "- Be decisive and avoid redundant delegation"
    )

    if global_instructions:
        instructions = f"{base_instructions}\n\n# Project Context\n{global_instructions}"
    else:
        instructions = base_instructions

    return client.as_agent(
        name="NextJsOrchestrator",
        instructions=instructions,
        description="Orchestrator for the Stitch-to-production React application pipeline. "
                    "Coordinates conversion of Google Stitch UI sketches into production-ready "
                    "Next.js 15+ applications using modern 2026 stack.",
    )


def build_workflow(
    agents_dir: str | None = None,
    platform: str | None = None,
    global_instructions_path: str | None = None,
    max_round_count: int = 25,
    max_stall_count: int = 4,
    intermediate_outputs: bool = True,
    enable_plan_review: bool = False,
):
    """
    Build and return the MagenticBuilder workflow for the Next.js pipeline.

    Args:
        agents_dir:               Path to agents directory (auto-detected if None).
        platform:                 Platform override: 'claude', 'cursor', 'copilot', 'generic'.
        global_instructions_path: Explicit path to global instructions file (auto-detected if None).
        max_round_count:          Max total agent turns before forced termination.
                                 Default: 25 (7 phases × ~3 turns per phase + buffer)
        max_stall_count:          Max consecutive no-progress rounds before early stop.
                                 Default: 4 (allows for retries on errors)
        intermediate_outputs:     Stream partial results as agents produce them.
        enable_plan_review:       Pause for human approval before execution.
    """
    # Auto-detect agents dir if not provided
    if agents_dir is None:
        for candidate in [".cursor/agents", ".claude/agents", ".copilot/agents", ".github/agents"]:
            if Path(candidate).exists():
                agents_dir = candidate
                break
        else:
            raise FileNotFoundError(
                "No agents directory found. Pass agents_dir= explicitly or create one of: "
                ".cursor/agents, .claude/agents, .copilot/agents"
            )

    registry = build_registry(agents_dir, platform, global_instructions_path)
    global_instructions = registry["global_instructions"]
    
    # Create MS agents from registry, excluding the orchestrator
    # (orchestrator will be the manager agent)
    local_ms_agents = {}
    orchestrator_data = None
    
    for name, data in registry["agents"].items():
        if "orchestrator" in name.lower():
            orchestrator_data = data
        else:
            local_ms_agents[name] = create_ms_agent(data, global_instructions)
    
    # Create manager agent (use orchestrator data if available, otherwise use default)
    if orchestrator_data:
        # Enhance orchestrator instructions with manager-specific guidance
        manager = build_manager_agent(global_instructions)
    else:
        manager = build_manager_agent(global_instructions)
    
    participants = list(local_ms_agents.values())

    workflow = MagenticBuilder(
        participants=participants,
        manager_agent=manager,
        intermediate_outputs=intermediate_outputs,
        max_round_count=max_round_count,
        max_stall_count=max_stall_count,
        enable_plan_review=enable_plan_review,
    ).build()

    print(f"[INFO] Next.js Pipeline Workflow built:")
    print(f"  - Manager: NextJsOrchestrator")
    print(f"  - Participants: {len(participants)} agents")
    for agent_name in local_ms_agents.keys():
        print(f"    • {agent_name}")
    print(f"  - Settings:")
    print(f"    • max_round_count: {max_round_count}")
    print(f"    • max_stall_count: {max_stall_count}")
    print(f"    • intermediate_outputs: {intermediate_outputs}")
    print(f"    • enable_plan_review: {enable_plan_review}")
    
    return workflow


# Default singleton — auto-detects agents dir from .cursor/agents
# Use build_workflow(agents_dir="...") when you need an explicit path or platform override.
workflow = build_workflow()

# Optional: expose workflow as a single agent (useful for nesting or Foundry deployment)
workflow_agent = workflow.as_agent(
    name="NextJsStitchPipeline",
    description=(
        "End-to-end pipeline that converts Google Stitch UI sketches into production-ready "
        "Next.js 15+ applications. Handles design token extraction, project scaffolding, "
        "component building, page assembly, data integration, quality polish, and deployment."
    )
)
