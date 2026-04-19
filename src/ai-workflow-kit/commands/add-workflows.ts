import { Command } from 'commander';
import chalk from 'chalk';
import { existsSync, readdirSync } from 'node:fs';
import * as path from 'node:path';
import { getResourceDir, getAvailableWorkflows } from '../lib/resources.js';
import { copyTree, copyFile } from '../lib/fs.js';
import { SKIP_DIRS } from '../lib/fs.js';
import type { CommandOptions } from '../lib/types.js';

/** Register the add-workflows subcommand on the given program. */
export function registerAddWorkflows(program: Command): void {
  program
    .command('add-workflows')
    .argument('<workflowName>', 'Name of the workflow to install')
    .description('Copy workflow template files to your project')
    .option('-o, --output <path>', 'Output directory', '.cursor/agents')
    .option('-f, --force', 'Overwrite existing files', false)
    .option('--dry-run', 'Show what would be copied without writing', false)
    .action((workflowName: string, opts: CommandOptions) => {
      try {
        executeAddWorkflows(workflowName, opts);
      } catch (err) {
        const msg = err instanceof Error ? err.message : String(err);
        console.error(chalk.red(`Error: ${msg}`));
        process.exitCode = 1;
      }
    });
}

function executeAddWorkflows(name: string, opts: CommandOptions): void {
  const available = getAvailableWorkflows();
  if (!available.includes(name)) {
    console.error(
      chalk.red(`Workflow '${name}' not found. Available workflows: ${available.join(', ')}`),
    );
    process.exitCode = 1;
    return;
  }

  const workflowsRoot = getResourceDir('workflows');
  const srcDir = path.join(workflowsRoot, name);
  const agentsSrc = path.join(srcDir, 'agents');
  const agentsDst = path.resolve(opts.output);
  const docsDir = path.resolve('docs', 'workflows', name);
  const hasAgents = existsSync(agentsSrc);

  if (opts.dryRun) {
    console.log(chalk.yellow('Dry run — no files will be written:\n'));
    if (hasAgents) {
      console.log(chalk.yellow(`  Agent files: ${rel(agentsSrc)} → ${rel(agentsDst)}`));
    }
    console.log(chalk.yellow(`  Docs:        ${rel(srcDir)} → ${rel(docsDir)}`));
    return;
  }

  const conflicts = collectConflicts(srcDir, agentsDst, docsDir, hasAgents);
  if (conflicts.length > 0 && !opts.force) {
    console.error(chalk.red('Destination conflicts found:'));
    for (const c of conflicts) {
      console.error(chalk.red(`  ${c}`));
    }
    console.error(chalk.red('\nUse --force to overwrite.'));
    process.exitCode = 1;
    return;
  }

  const written: string[] = [];

  if (hasAgents) {
    for (const entry of readdirSync(agentsSrc, { withFileTypes: true })) {
      if (!entry.isFile()) continue;
      const s = path.join(agentsSrc, entry.name);
      const d = path.join(agentsDst, entry.name);
      written.push(copyFile(s, d));
    }
  }

  for (const entry of readdirSync(srcDir, { withFileTypes: true })) {
    if (entry.name === 'agents') continue;
    if (SKIP_DIRS.has(entry.name)) continue;
    const s = path.join(srcDir, entry.name);
    const d = path.join(docsDir, entry.name);
    if (entry.isDirectory()) {
      written.push(...copyTree(s, d));
    } else if (entry.isFile()) {
      written.push(copyFile(s, d));
    }
  }

  printSuccess(written);
}

function collectConflicts(
  srcDir: string,
  agentsDst: string,
  docsDir: string,
  hasAgents: boolean,
): string[] {
  const conflicts: string[] = [];
  if (hasAgents) {
    const agentsSrc = path.join(srcDir, 'agents');
    for (const entry of readdirSync(agentsSrc, { withFileTypes: true })) {
      if (!entry.isFile()) continue;
      const dest = path.join(agentsDst, entry.name);
      if (existsSync(dest)) conflicts.push(rel(dest));
    }
  }
  if (existsSync(docsDir)) {
    conflicts.push(rel(docsDir));
  }
  return conflicts;
}

function printSuccess(written: string[]): void {
  console.log(chalk.green(`\n✔ Successfully copied ${written.length} file(s):\n`));
  for (const f of written) {
    console.log(chalk.green(`  ${rel(f)}`));
  }
}

function rel(absPath: string): string {
  return path.relative(process.cwd(), absPath);
}
