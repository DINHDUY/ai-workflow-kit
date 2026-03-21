import { describe, it, after } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, existsSync, readFileSync, rmSync } from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { execFileSync } from 'node:child_process';
import { findCommandMd } from '../../commands/add-commands.js';
import { getResourceDir } from '../../lib/resources.js';

const CLI_PATH = path.resolve('src/ai-workflow-kit/cli.ts');

function runCli(args: string[], cwd: string): { stdout: string; stderr: string; exitCode: number } {
  try {
    const stdout = execFileSync('npx', ['tsx', CLI_PATH, ...args], {
      cwd,
      encoding: 'utf8',
      env: { ...process.env, NODE_NO_WARNINGS: '1' },
      timeout: 30000,
    });
    return { stdout, stderr: '', exitCode: 0 };
  } catch (err: unknown) {
    const e = err as { stdout?: string; stderr?: string; status?: number };
    return {
      stdout: e.stdout ?? '',
      stderr: e.stderr ?? '',
      exitCode: e.status ?? 1,
    };
  }
}

describe('findCommandMd', () => {
  it('should locate the .md file inside a command bundle', () => {
    const commandsRoot = getResourceDir('commands');
    const bundlePath = path.join(commandsRoot, 'abc');
    const mdPath = findCommandMd(bundlePath, 'abc');
    assert.ok(mdPath.endsWith('abc.md'));
    assert.ok(existsSync(mdPath));
  });

  it('should throw for missing .md file', () => {
    let tmpDir: string | undefined;
    try {
      tmpDir = mkdtempSync(path.join(os.tmpdir(), 'awkit-cmd-'));
      mkdirSync(path.join(tmpDir, 'empty-cmd'), { recursive: true });
      assert.throws(
        () => findCommandMd(path.join(tmpDir!, 'empty-cmd'), 'empty-cmd'),
        (err: unknown) => {
          assert.ok(err instanceof Error);
          assert.ok(err.message.includes('empty-cmd.md'));
          return true;
        }
      );
    } finally {
      if (tmpDir) rmSync(tmpDir, { recursive: true, force: true });
    }
  });
});

describe('add-commands command', () => {
  let tmpDir: string;

  after(() => {
    if (tmpDir) rmSync(tmpDir, { recursive: true, force: true });
  });

  it('should copy .md file to default output directory', () => {
    tmpDir = mkdtempSync(path.join(os.tmpdir(), 'awkit-addcmds-'));
    const outDir = path.join(tmpDir, '.cursor', 'commands');
    const result = runCli(['add-commands', 'abc', '--output', outDir], tmpDir);

    assert.equal(result.exitCode, 0, `stderr: ${result.stderr}`);
    assert.ok(existsSync(path.join(outDir, 'abc.md')));
  });

  it('should copy scripts/ to project root scripts/', () => {
    tmpDir = mkdtempSync(path.join(os.tmpdir(), 'awkit-addcmds-'));
    const outDir = path.join(tmpDir, '.cursor', 'commands');
    const result = runCli(['add-commands', 'send-email', '--output', outDir], tmpDir);

    assert.equal(result.exitCode, 0, `stderr: ${result.stderr}`);
    assert.ok(existsSync(path.join(tmpDir, 'scripts', 'python', 'send_email.py')));
  });

  it('should print planned operations in dry-run mode without creating files', () => {
    tmpDir = mkdtempSync(path.join(os.tmpdir(), 'awkit-addcmds-'));
    const outDir = path.join(tmpDir, '.cursor', 'commands');
    const result = runCli(['add-commands', 'abc', '--output', outDir, '--dry-run'], tmpDir);

    assert.equal(result.exitCode, 0);
    assert.ok(result.stdout.includes('Dry run'));
    assert.ok(!existsSync(path.join(outDir, 'abc.md')));
  });

  it('should overwrite existing .md with --force', () => {
    tmpDir = mkdtempSync(path.join(os.tmpdir(), 'awkit-addcmds-'));
    const outDir = path.join(tmpDir, '.cursor', 'commands');
    mkdirSync(outDir, { recursive: true });
    writeFileSync(path.join(outDir, 'abc.md'), 'old');

    const result = runCli(['add-commands', 'abc', '--output', outDir, '--force'], tmpDir);

    assert.equal(result.exitCode, 0, `stderr: ${result.stderr}`);
    const content = readFileSync(path.join(outDir, 'abc.md'), 'utf8');
    assert.notEqual(content, 'old');
  });

  it('should detect conflict on .md path and exit 1 without --force', () => {
    tmpDir = mkdtempSync(path.join(os.tmpdir(), 'awkit-addcmds-'));
    const outDir = path.join(tmpDir, '.cursor', 'commands');
    mkdirSync(outDir, { recursive: true });
    writeFileSync(path.join(outDir, 'abc.md'), 'old');

    const result = runCli(['add-commands', 'abc', '--output', outDir], tmpDir);

    assert.notEqual(result.exitCode, 0);
    const output = result.stdout + result.stderr;
    assert.ok(output.includes('already exists') || output.includes('conflict'));
  });

  it('should exit 1 with available list for invalid command name', () => {
    tmpDir = mkdtempSync(path.join(os.tmpdir(), 'awkit-addcmds-'));
    const result = runCli(['add-commands', 'nonexistent-command-xyz'], tmpDir);

    assert.notEqual(result.exitCode, 0);
    const output = result.stdout + result.stderr;
    assert.ok(output.includes('not found'));
    assert.ok(output.includes('abc'));
  });

  it('should copy .md to custom output directory with --output', () => {
    tmpDir = mkdtempSync(path.join(os.tmpdir(), 'awkit-addcmds-'));
    const customOut = path.join(tmpDir, 'my-cmds');
    const result = runCli(['add-commands', 'abc', '--output', customOut], tmpDir);

    assert.equal(result.exitCode, 0, `stderr: ${result.stderr}`);
    assert.ok(existsSync(path.join(customOut, 'abc.md')));
  });
});
