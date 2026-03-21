import { fileURLToPath } from 'node:url';
import { existsSync, readdirSync } from 'node:fs';
import * as path from 'node:path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Locate a top-level bundled resource directory using a two-phase lookup.
 * Phase 1 (installed): resolves relative to compiled output inside node_modules.
 * Phase 2 (development): walks up from source to the repository root.
 */
export function getResourceDir(name: string): string {
  // Phase 1 — installed package: resources sit alongside dist/ at package root
  const pkgDir = path.resolve(__dirname, '..', '..', name);
  if (existsSync(pkgDir)) return pkgDir;

  // Phase 2 — development: repository root is three levels up from src/ai-workflow-kit/lib/
  const devDir = path.resolve(__dirname, '..', '..', '..', name);
  if (existsSync(devDir)) return devDir;

  throw new Error(
    `Resource directory '${name}' not found. Package may be corrupted.`
  );
}

/** Return sorted names of available skill directories. */
export function getAvailableSkills(): string[] {
  const dir = getResourceDir('skills');
  return readdirSync(dir, { withFileTypes: true })
    .filter((e) => e.isDirectory())
    .map((e) => e.name)
    .sort();
}

/** Return sorted names of available command directories. */
export function getAvailableCommands(): string[] {
  const dir = getResourceDir('commands');
  return readdirSync(dir, { withFileTypes: true })
    .filter((e) => e.isDirectory())
    .map((e) => e.name)
    .sort();
}

/** Return sorted names of available workflow directories. */
export function getAvailableWorkflows(): string[] {
  const dir = getResourceDir('workflows');
  return readdirSync(dir, { withFileTypes: true })
    .filter((e) => e.isDirectory())
    .map((e) => e.name)
    .sort();
}
