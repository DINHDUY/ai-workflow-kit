# Frontend-Stitch Pipeline

Convert Google Stitch exports (rough HTML/CSS + PNG screenshots) into production-quality frontend code using a 5-phase multi-agent pipeline.

## Overview

Google Stitch is an AI UI design tool that generates HTML/CSS landing pages and PNG screenshots. These artifacts are starting points, not production code. The frontend-stitch pipeline automates the conversion of these rough exports into clean, maintainable frontend code using a modern framework and design system.

**Core philosophy**: Treat Stitch as a fast design generator and spec provider, then rebuild cleanly in your own stack.

## Agents

| Agent | Role | Phase |
|-------|------|-------|
| `frontend-stitch.orchestrator` | Coordinates the full pipeline | All |
| `frontend-stitch.analyzer` | Analyzes Stitch HTML + PNG artifacts | Phase 1 |
| `frontend-stitch.architect` | Designs target architecture & component model | Phase 2 |
| `frontend-stitch.builder` | Implements complete frontend code | Phase 3 |
| `frontend-stitch.hardener` | Hardens for production (tests, CI/CD, a11y) | Phase 4 |

## Pipeline Phases

### Phase 1: Artifact Analysis (`frontend-stitch.analyzer`)

Ingests Stitch HTML and PNG exports, then produces:
- **Analysis report** -- structural survey, CSS analysis, layout patterns
- **Component inventory** -- atoms, molecules, organisms catalog
- **Design tokens** -- colors, typography, spacing, radii, shadows
- **Gaps report** -- responsiveness and accessibility issues to fix

### Phase 2: Architecture Design (`frontend-stitch.architect`)

Transforms analysis into a production blueprint:
- **Architecture spec** -- framework setup, project structure, routing
- **Design tokens** -- finalized Tailwind config and CSS variables
- **Component model** -- API contracts with props and TypeScript interfaces
- **Page routes** -- page and layout hierarchy
- **Handoff document** -- concise summary for the builder

### Phase 3: Component Building (`frontend-stitch.builder`)

Implements the complete frontend application:
- Framework scaffolding (package.json, tsconfig, Tailwind config)
- All atom components (Button, TextField, Icon, Badge, Avatar)
- All molecule components (FeatureCard, TestimonialCard, PricingTier)
- All organism components (HeroSection, FeatureSection, TestimonialsSection)
- Layout components (AppShell, Navbar, Footer)
- Page assembly with placeholder data matching the Stitch design

### Phase 4: Production Hardening (`frontend-stitch.hardener`)

Hardens the built frontend for production:
- Responsive breakpoints across all components
- Accessibility fixes (semantic HTML, ARIA, keyboard navigation, color contrast)
- Loading, error, and empty states for data-bound components
- Unit tests (React Testing Library)
- E2E tests (Playwright)
- Linting and formatting (ESLint, Prettier)
- CI/CD pipeline (GitHub Actions)
- Visual regression baseline from original Stitch PNGs

### Phase 5: Quality Review (`frontend-stitch.orchestrator`)

The orchestrator performs a final quality review:
- Visual regression against original Stitch screenshots
- Accessibility audit
- Code quality checks (linting, type-checking)
- Responsiveness verification across breakpoints
- Pass/fail report with specific issues

## Quick Start

1. **Run the orchestrator**:
   ```
   Use frontend-stitch.orchestrator with Stitch HTML and PNG files
   ```

2. **Or run individual agents**:
   ```
   Use frontend-stitch.analyzer to analyze Stitch artifacts
   Use frontend-stitch.architect to design the architecture
   Use frontend-stitch.builder to implement the frontend
   Use frontend-stitch.hardener to harden for production
   ```

## Default Stack

- Framework: Next.js 15 (App Router)
- Language: TypeScript
- Styling: Tailwind CSS
- Testing: React Testing Library + Playwright
- Linting: ESLint + Prettier
- CI/CD: GitHub Actions

## Project Structure

```
project-root/
├── src/
│   ├── app/
│   │   ├── layout.tsx          # Root layout with AppShell
│   │   ├── page.tsx            # Home page
│   │   └── globals.css         # Tailwind + CSS variables
│   ├── components/
│   │   ├── atoms/              # Button, TextField, Icon, Badge, Avatar
│   │   ├── molecules/          # FeatureCard, TestimonialCard, PricingTier
│   │   ├── organisms/          # HeroSection, FeatureSection, etc.
│   │   └── layout/             # AppShell, Navbar, Footer
│   ├── hooks/                  # Custom React hooks
│   ├── lib/                    # Utilities, API clients
│   └── types/                  # TypeScript definitions
├── tests/
│   ├── unit/                   # Component tests
│   ├── e2e/                    # Playwright tests
│   └── screenshots/            # Visual regression baselines
├── tailwind.config.ts          # Tailwind with design tokens
├── package.json
├── tsconfig.json
└── .github/workflows/ci.yml    # CI/CD pipeline
```

## File Structure

```
workflows/frontend-stitch/
├── README.md                           # This file
├── frontend-stitch-plan.md             # Multi-agent plan document
├── stich.md                            # Research document
└── agents/
    ├── frontend-stitch.orchestrator.md # Pipeline orchestrator
    ├── frontend-stitch.analyzer.md     # Artifact analyzer
    ├── frontend-stitch.architect.md    # Architecture designer
    ├── frontend-stitch.builder.md      # Component builder
    └── frontend-stitch.hardener.md     # Production hardener
```

## References

- [Google Stitch to AI Studio: Design-to-Code Workflow](https://mindstudio.ai/blog/google-stitch-to-ai-studio-design-to-code-workflow)
- [Google Stitch Tutorial & Prompts Guide](https://0xminds.com/blog/guides/google-stitch-tutorial-prompts-guide)
- [Code Meets Creativity: Using Google Stitch as a Frontend Developer](https://dev.to/asmaa-almadhoun/code-meets-creativity-using-google-stitch-as-a-frontend-developer-1997)
- [Google Stitch Anti-Gravity Guide](https://antigravity.codes/blog/google-stitch-antigravity-guide)
