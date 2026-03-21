# Review Checklist

This checklist provides comprehensive criteria for evaluating agent skills across all platforms. Use it to systematically review SKILL.md files, directory structure, metadata, content quality, and platform compatibility.


## AI Agent Skill Review Checklist (Universal)
*Compatible with Claude Code, Cursor, and other Agent Skills Standard-compliant platforms*

### Platform & Directory Structure
- [ ] **Skill location** follows platform conventions:
  - **Claude Code**: `.claude/skills/` (project) or global skill directory
  - **Cursor**: `.cursor/skills/` (project) or `~/.cursor/skills/` (personal)
  - **Do NOT use**: `~/.cursor/skills-cursor/` (reserved for Cursor built-in skills)
  - **Universal**: Compatible with Agent Skills Standard for portability
  
- [ ] **Directory structure** is correct:
  - Skill folder name matches skill `name` field (lowercase, hyphens)
  - SKILL.md file exists in root of skill directory
  - Optional: `scripts/`, `references/`, `templates/` subdirectories
  - Optional: `README.md` for human documentation

### YAML Frontmatter & Metadata
- [ ] **Name field** is present and valid
  - Maximum 64 characters
  - Contains only lowercase letters, numbers, and hyphens
  - No XML tags
  - No reserved words ("anthropic", "claude")
  - Uses gerund form (e.g., "processing-pdfs") or consistent naming pattern
  - **Cursor**: Directory name must match the name field
  
- [ ] **Description field** is present and valid
  - Non-empty, maximum 1024 characters
  - No XML tags
  - Written in third person (not "I can help" or "You can use")
  - Specific and includes key terms
  - Describes BOTH what the skill does AND when to use it
  - Includes trigger keywords/contexts for intent matching
  - Lists explicit action verbs users might say
  - Specifies the domain clearly
  - Includes use-case variations

### Optional Metadata (Extended)
- [ ] **Skill categorization** (if using skill packs or organization):
  - Category field specified (e.g., "development", "testing", "writing")
  - Tags provided for filtering
  - `alwaysApply: true` flag if skill should always be available

### Content Quality & Conciseness
- [ ] **SKILL.md body** is under 500 lines
- [ ] Content is **concise** - no unnecessary explanations
- [ ] Assumes agent already knows general concepts
- [ ] Every piece of information justifies its token cost
- [ ] No over-explanations of basic concepts
- [ ] Consistent terminology throughout (no mixing synonyms)
- [ ] First line of description becomes skill summary (Cursor convention)

### Structure & Organization
- [ ] **Progressive disclosure** is properly implemented
  - Complex content split into separate files when needed
  - SKILL.md serves as overview/table of contents
  - Additional files referenced but not nested too deeply
  
- [ ] **File references** are one level deep from SKILL.md (not deeply nested)
- [ ] Longer reference files (>100 lines) include table of contents at top
- [ ] All file paths use forward slashes (no Windows-style backslashes)
- [ ] Files have descriptive names (not "doc1.md", "file2.md")
- [ ] Directory follows standard subdirectory conventions:
  - `references/` for detailed documentation
  - `scripts/` for automation and executable tools
  - `templates/` for boilerplate code/files
  - `examples/` for practical demonstrations

### Degrees of Freedom
- [ ] Appropriate level of specificity for the task
  - High freedom (text instructions) for flexible tasks
  - Medium freedom (pseudocode) for preferred patterns
  - Low freedom (exact scripts) for fragile operations
  
- [ ] Guidance matches task fragility and variability

### Workflows & Feedback Loops
- [ ] Complex tasks broken into clear, sequential steps
- [ ] Workflows include **copy-able checklists** for progress tracking
- [ ] **Feedback loops** implemented for critical operations
  - Validation steps included
  - Clear "run validator → fix errors → repeat" patterns
  
- [ ] Conditional workflows guide decision points clearly
- [ ] Only proceeds when validation passes

### Content Guidelines
- [ ] **No time-sensitive information** (or properly marked in "old patterns" section)
- [ ] **Old/deprecated patterns** in collapsible sections with clear labels
- [ ] No assumptions about future dates or deadlines
- [ ] Examples are concrete, not abstract
- [ ] Uses third-person perspective throughout
- [ ] Clear "do's and don'ts" when appropriate

### Common Patterns
- [ ] **Templates** provided where appropriate
  - Strictness matches requirements (strict for APIs, flexible for creative tasks)
  
- [ ] **Examples** included for quality-dependent outputs
  - Input/output pairs provided
  - Multiple examples showing variation
  
- [ ] **Conditional workflows** guide through decision points clearly
- [ ] Provides default approach with escape hatches (not overwhelming options)

### Code & Scripts (if applicable)
- [ ] **Scripts solve problems** rather than punting to agent
- [ ] Error handling is **explicit and helpful**
  - Handles FileNotFoundError
  - Handles PermissionError
  - Provides alternatives instead of failing
  
- [ ] **No "voodoo constants"** - all configuration values documented
- [ ] Required packages **explicitly listed**
- [ ] Package availability **verified** in code execution environment
- [ ] Scripts have clear documentation
- [ ] **Clear execution intent** specified
  - "Run script.py" for execution
  - "See script.py for algorithm" for reference
  
- [ ] Utility scripts provided for deterministic operations
- [ ] Visual analysis used when inputs can be rendered as images
- [ ] **Portable script execution**:
  - Scripts work identically across platforms
  - No platform-specific dependencies assumed
  - Entry point is clear (e.g., `scripts/main.py`)

### Validation & Verification
- [ ] **Verifiable intermediate outputs** for complex tasks
- [ ] Validation scripts included for critical operations
- [ ] Plan-validate-execute pattern for batch/destructive operations
- [ ] Validation scripts provide verbose, specific error messages

### MCP & Tools (if applicable)
- [ ] MCP tools use **fully qualified names** (ServerName:tool_name)
- [ ] No assumptions about tool installation
- [ ] Installation instructions provided when needed
- [ ] Tool dependencies clearly documented

### Platform Compatibility
- [ ] **Agent Skills Standard compliance** (for portability):
  - SKILL.md format follows specification
  - Skill works identically across all AI clients
  - No prohibited platform-specific dependencies
  - Can be installed via standard skill managers
  
- [ ] **Discovery mechanism** works correctly:
  - Description enables semantic intent matching
  - Agent can identify when to activate skill
  - Name is unique in skill registry
  
- [ ] **Cursor-specific** (if targeting Cursor):
  - Compatible with skill pack system
  - Can be enabled/disabled via pack definitions
  - Works with Cursor's MCP server integration
  
- [ ] **Claude Code-specific** (if targeting Claude):
  - Works in code execution environment
  - Compatible with Claude's progressive disclosure model

### Anti-Patterns (verify NONE present)
- [ ] ✓ No Windows-style paths (backslashes)
- [ ] ✓ No overwhelming number of option choices
- [ ] ✓ No punting to agent instead of handling errors
- [ ] ✓ No magic numbers or undocumented constants
- [ ] ✓ No time-sensitive information without proper marking
- [ ] ✓ No inconsistent terminology
- [ ] ✓ No deeply nested file references (>1 level)
- [ ] ✓ No vague or generic names/descriptions
- [ ] ✓ Directory name doesn't start with `.` or `_` (platform requirement)

### Testing & Validation
- [ ] **At least 3 evaluations created** before extensive documentation
- [ ] Tested with **all intended models** (Haiku, Sonnet, Opus, or platform-specific models)
- [ ] Tested with **real usage scenarios** (not just test cases)
- [ ] Skill activates when expected based on description
- [ ] Instructions are clear to actual users
- [ ] Team feedback incorporated (if applicable)
- [ ] **Cross-platform testing** (if targeting multiple platforms):
  - Verified in Cursor
  - Verified in Claude Code
  - Verified in other target platforms

### Evaluation-Driven Development
- [ ] Gaps identified through actual agent usage
- [ ] Evaluations created to test specific gaps
- [ ] Baseline performance measured without skill
- [ ] Minimal instructions written to pass evaluations
- [ ] Iterative refinement based on evaluation results

### Observational Testing
- [ ] Observed how agent navigates the skill
- [ ] Checked for unexpected exploration paths
- [ ] Verified references are followed correctly
- [ ] Confirmed no files are consistently ignored
- [ ] Validated metadata triggers skill appropriately
- [ ] Verified skill discovery works (agent finds skill when needed)

### Documentation Completeness
- [ ] Purpose and use cases clearly explained
- [ ] Prerequisites and dependencies listed
- [ ] Usage examples provided
- [ ] Error handling documented
- [ ] Limitations noted (if any)
- [ ] Optional README.md for human readers (complementing SKILL.md for agents)

### Version Control & Sharing
- [ ] **Skill is ready for version control**:
  - No generated or temporary files included
  - `.gitignore` configured if needed
  - Clear commit message conventions if contributing
  
- [ ] **Installable via standard methods**:
  - Can be cloned from GitHub
  - Works with skill CLI tools (Vercel, skillport, etc.)
  - Installation instructions provided
  
- [ ] **Team collaboration ready**:
  - Documentation explains skill purpose to team members
  - Contribution guidelines included (if open source)
  - License specified (if applicable)

### Portability Checklist (Agent Skills Standard)
- [ ] **Write-once, run-anywhere compatibility**:
  - No hardcoded platform assumptions
  - Uses standard SKILL.md format
  - Scripts are platform-agnostic
  - File paths are relative and portable
  
- [ ] **Installation compatibility**:
  - Can be installed via: GitHub clone, skill CLI, zip file, local path
  - Skill ID is unique across potential repositories
  - Priority resolution works correctly (project > agent > global > bundled)

---

## Review Summary Checklist
- [ ] All technical requirements met (name, description format)
- [ ] Content is concise and assumes agent's intelligence
- [ ] Structure enables progressive disclosure
- [ ] Appropriate freedom level for task complexity
- [ ] Workflows and validation patterns implemented
- [ ] No anti-patterns present
- [ ] Comprehensive testing completed
- [ ] Platform compatibility verified
- [ ] Ready for deployment and sharing

**Target Platform(s):**
- [ ] Claude Code
- [ ] Cursor
- [ ] Other (specify): _____________

**Notes/Issues Found:**
_[Space for reviewer to note specific issues or improvements needed]_

**Portability Score:**
- [ ] Single-platform only (works on one platform)
- [ ] Multi-platform compatible (works on 2+ platforms)
- [ ] Agent Skills Standard compliant (works everywhere)

---

## Key Updates from Cursor Documentation

The updated checklist now includes:

1. **Platform-specific directory conventions** for both Claude Code and Cursor
2. **Agent Skills Standard compliance** checks for portability
3. **Skill pack compatibility** for Cursor's skill management system
4. **Intent matching requirements** for better skill discovery
5. **Cross-platform testing** recommendations
6. **Portability assessment** section
7. **Installation compatibility** verification
8. **Directory naming restrictions** (no leading `.` or `_`)
9. **Version control readiness** checks
10. **Standard subdirectory conventions** (references/, scripts/, templates/)

The checklist maintains all original Claude/Anthropic best practices while adding compatibility layers for Cursor and other Agent Skills Standard-compliant platforms.