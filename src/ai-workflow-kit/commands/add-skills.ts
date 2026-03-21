import { Command } from 'commander';
import chalk from 'chalk';
import { existsSync, readdirSync } from 'node:fs';
import * as path from 'node:path';
import { getResourceDir, getAvailableSkills } from '../lib/resources.js';
import { copyTree, copyFile } from '../lib/fs.js';
import type { CommandOptions } from '../lib/types.js';

/** Register the add-skills subcommand on the given program. */
export function registerAddSkills(program: Command): void {
  program
    .command('add-skills')
    .argument('<skillName>', 'Name of the skill to install')
    .description('Copy skill template files to your project')
    .option('-o, --output <path>', 'Output directory', 'skills')
    .option('-f, --force', 'Overwrite existing files', false)
    .option('--dry-run', 'Show what would be copied without writing', false)
    .action((skillName: string, opts: CommandOptions) => {
      try {
        executeAddSkills(skillName, opts);
      } catch (err) {
        const msg = err instanceof Error ? err.message : String(err);
        console.error(chalk.red(`Error: ${msg}`));
        process.exitCode = 1;
      }
    });
}

function executeAddSkills(name: string, opts: CommandOptions): void {
  const available = getAvailableSkills();
  if (!available.includes(name)) {
    console.error(
      chalk.red(`Skill '${name}' not found. Available skills: ${available.join(', ')}`)
    );
    process.exitCode = 1;
    return;
  }

  const skillsRoot = getResourceDir('skills');
  const srcDir = path.join(skillsRoot, name);
  const dstDir = path.resolve(opts.output, name);
  const scriptsSrc = path.join(srcDir, 'scripts');
  const scriptsDst = path.resolve('scripts');
  const hasScripts = existsSync(scriptsSrc);

  if (opts.dryRun) {
    console.log(chalk.yellow('Dry run — no files will be written:\n'));
    console.log(chalk.yellow(`  Skill files: ${rel(srcDir)} → ${rel(dstDir)}`));
    if (hasScripts) {
      console.log(chalk.yellow(`  Scripts:     ${rel(scriptsSrc)} → ${rel(scriptsDst)}`));
    }
    return;
  }

  if (existsSync(dstDir) && !opts.force) {
    console.error(
      chalk.red(
        `Destination already exists: ${rel(dstDir)}. Use --force to overwrite.`
      )
    );
    process.exitCode = 1;
    return;
  }

  const written: string[] = [];
  for (const entry of readdirSync(srcDir, { withFileTypes: true })) {
    if (entry.name === 'scripts') continue;
    const s = path.join(srcDir, entry.name);
    const d = path.join(dstDir, entry.name);
    if (entry.isDirectory()) {
      written.push(...copyTree(s, d));
    } else if (entry.isFile()) {
      written.push(copyFile(s, d));
    }
  }

  if (hasScripts) {
    written.push(...copyTree(scriptsSrc, scriptsDst));
  }

  printSuccess(written);
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
