import { Command } from 'commander';
import chalk from 'chalk';
import { existsSync } from 'node:fs';
import * as path from 'node:path';
import { getResourceDir, getAvailableCommands } from '../lib/resources.js';
import { copyTree, copyFile } from '../lib/fs.js';
import type { CommandOptions } from '../lib/types.js';

/** Locate the <commandName>.md file inside a command bundle directory. */
export function findCommandMd(bundlePath: string, commandName: string): string {
  const mdFile = path.join(bundlePath, `${commandName}.md`);
  if (!existsSync(mdFile)) {
    throw new Error(`No '${commandName}.md' found in command bundle at ${bundlePath}.`);
  }
  return mdFile;
}

/** Register the add-commands subcommand on the given program. */
export function registerAddCommands(program: Command): void {
  program
    .command('add-commands')
    .argument('<commandName>', 'Name of the command to install')
    .description('Copy command template files to your project')
    .option('-o, --output <path>', 'Output directory', '.cursor/commands')
    .option('-f, --force', 'Overwrite existing files', false)
    .option('--dry-run', 'Show what would be copied without writing', false)
    .action((commandName: string, opts: CommandOptions) => {
      try {
        executeAddCommands(commandName, opts);
      } catch (err) {
        const msg = err instanceof Error ? err.message : String(err);
        console.error(chalk.red(`Error: ${msg}`));
        process.exitCode = 1;
      }
    });
}

function executeAddCommands(name: string, opts: CommandOptions): void {
  const available = getAvailableCommands();
  if (!available.includes(name)) {
    console.error(
      chalk.red(`Command '${name}' not found. Available commands: ${available.join(', ')}`),
    );
    process.exitCode = 1;
    return;
  }

  const commandsRoot = getResourceDir('commands');
  const bundleDir = path.join(commandsRoot, name);
  const mdSrc = findCommandMd(bundleDir, name);
  const mdDst = path.resolve(opts.output, `${name}.md`);
  const scriptsSrc = path.join(bundleDir, 'scripts');
  const scriptsDst = path.resolve('scripts');
  const hasScripts = existsSync(scriptsSrc);

  if (opts.dryRun) {
    console.log(chalk.yellow('Dry run — no files will be written:\n'));
    console.log(chalk.yellow(`  Command file: ${rel(mdSrc)} → ${rel(mdDst)}`));
    if (hasScripts) {
      console.log(chalk.yellow(`  Scripts:      ${rel(scriptsSrc)} → ${rel(scriptsDst)}`));
    }
    return;
  }

  if (existsSync(mdDst) && !opts.force) {
    console.error(
      chalk.red(`Destination already exists: ${rel(mdDst)}. Use --force to overwrite.`),
    );
    process.exitCode = 1;
    return;
  }

  const written: string[] = [];
  written.push(copyFile(mdSrc, mdDst));

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
