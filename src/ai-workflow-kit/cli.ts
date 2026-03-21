#!/usr/bin/env node
import { Command } from 'commander';
import { registerAddSkills } from './commands/add-skills.js';
import { registerAddCommands } from './commands/add-commands.js';
import { registerAddWorkflows } from './commands/add-workflows.js';

const program = new Command()
  .name('ai-workflow-kit')
  .description('Scaffold AI agent assets into your project')
  .version(process.env.npm_package_version ?? '0.0.0');

registerAddSkills(program);
registerAddCommands(program);
registerAddWorkflows(program);

program.parse();
