import { describe, it, after } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, existsSync, readFileSync, rmSync } from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { execFileSync } from 'node:child_process';

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

describe('add-skills command', () => {
  let tmpDir: string;

  after(() => {
    if (tmpDir) rmSync(tmpDir, { recursive: true, force: true });
  });

  it('should copy skill files to default output directory', () => {
    tmpDir = mkdtempSync(path.join(os.tmpdir(), 'awkit-addskills-'));
    const result = runCli(['add-skills', 'TEMPLATE', '--output', path.join(tmpDir, 'skills')], tmpDir);

    assert.equal(result.exitCode, 0, `stderr: ${result.stderr}`);
    assert.ok(existsSync(path.join(tmpDir, 'skills', 'TEMPLATE', 'SKILL.md')));
    assert.ok(existsSync(path.join(tmpDir, 'skills', 'TEMPLATE', 'README.md')));
  });

  it('should copy scripts/ to project root scripts/', () => {
    tmpDir = mkdtempSync(path.join(os.tmpdir(), 'awkit-addskills-'));
    const result = runCli(['add-skills', 'TEMPLATE', '--output', path.join(tmpDir, 'skills')], tmpDir);

    assert.equal(result.exitCode, 0, `stderr: ${result.stderr}`);
    assert.ok(existsSync(path.join(tmpDir, 'scripts', 'example.sh')));
    assert.ok(existsSync(path.join(tmpDir, 'scripts', 'validate.py')));
  });

  it('should print planned operations in dry-run mode without creating files', () => {
    tmpDir = mkdtempSync(path.join(os.tmpdir(), 'awkit-addskills-'));
    const result = runCli(['add-skills', 'TEMPLATE', '--output', path.join(tmpDir, 'skills'), '--dry-run'], tmpDir);

    assert.equal(result.exitCode, 0);
    assert.ok(result.stdout.includes('Dry run'));
    assert.ok(!existsSync(path.join(tmpDir, 'skills', 'TEMPLATE')));
  });

  it('should overwrite existing files with --force', () => {
    tmpDir = mkdtempSync(path.join(os.tmpdir(), 'awkit-addskills-'));
    const destDir = path.join(tmpDir, 'skills', 'TEMPLATE');
    mkdirSync(destDir, { recursive: true });
    writeFileSync(path.join(destDir, 'SKILL.md'), 'old');

    const result = runCli(['add-skills', 'TEMPLATE', '--output', path.join(tmpDir, 'skills'), '--force'], tmpDir);

    assert.equal(result.exitCode, 0, `stderr: ${result.stderr}`);
    const content = readFileSync(path.join(destDir, 'SKILL.md'), 'utf8');
    assert.notEqual(content, 'old');
  });

  it('should detect conflicts without --force and exit 1', () => {
    tmpDir = mkdtempSync(path.join(os.tmpdir(), 'awkit-addskills-'));
    const destDir = path.join(tmpDir, 'skills', 'TEMPLATE');
    mkdirSync(destDir, { recursive: true });
    writeFileSync(path.join(destDir, 'SKILL.md'), 'old');

    const result = runCli(['add-skills', 'TEMPLATE', '--output', path.join(tmpDir, 'skills')], tmpDir);

    assert.notEqual(result.exitCode, 0);
    const output = result.stdout + result.stderr;
    assert.ok(output.includes('already exists') || output.includes('conflict'));
  });

  it('should exit 1 with available list for invalid skill name', () => {
    tmpDir = mkdtempSync(path.join(os.tmpdir(), 'awkit-addskills-'));
    const result = runCli(['add-skills', 'nonexistent-skill-xyz'], tmpDir);

    assert.notEqual(result.exitCode, 0);
    const output = result.stdout + result.stderr;
    assert.ok(output.includes('not found'));
    assert.ok(output.includes('TEMPLATE'));
  });

  it('should copy to custom output directory with --output', () => {
    tmpDir = mkdtempSync(path.join(os.tmpdir(), 'awkit-addskills-'));
    const customOut = path.join(tmpDir, 'my-custom-skills');
    const result = runCli(['add-skills', 'TEMPLATE', '--output', customOut], tmpDir);

    assert.equal(result.exitCode, 0, `stderr: ${result.stderr}`);
    assert.ok(existsSync(path.join(customOut, 'TEMPLATE', 'SKILL.md')));
  });
});
