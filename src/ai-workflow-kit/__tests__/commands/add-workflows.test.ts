import { describe, it, after } from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, existsSync, rmSync } from 'node:fs';
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

describe('add-workflows command', () => {
  let tmpDir: string;

  after(() => {
    if (tmpDir) rmSync(tmpDir, { recursive: true, force: true });
  });

  it('should copy agent files flat to output dir and docs to docs/workflows/<name>/', () => {
    tmpDir = mkdtempSync(path.join(os.tmpdir(), 'awkit-addwf-'));
    const agentsOut = path.join(tmpDir, '.cursor', 'agents');
    const result = runCli(['add-workflows', 'speckit', '--output', agentsOut], tmpDir);

    assert.equal(result.exitCode, 0, `stderr: ${result.stderr}`);
    assert.ok(existsSync(path.join(agentsOut, 'speckit-overlay.orchestrator.md')));
    assert.ok(existsSync(path.join(tmpDir, 'docs', 'workflows', 'speckit')));
  });

  it('should print planned operations in dry-run mode without creating files', () => {
    tmpDir = mkdtempSync(path.join(os.tmpdir(), 'awkit-addwf-'));
    const agentsOut = path.join(tmpDir, '.cursor', 'agents');
    const result = runCli(['add-workflows', 'speckit', '--output', agentsOut, '--dry-run'], tmpDir);

    assert.equal(result.exitCode, 0);
    assert.ok(result.stdout.includes('Dry run'));
    assert.ok(!existsSync(agentsOut));
  });

  it('should overwrite existing files with --force', () => {
    tmpDir = mkdtempSync(path.join(os.tmpdir(), 'awkit-addwf-'));
    const agentsOut = path.join(tmpDir, '.cursor', 'agents');
    mkdirSync(agentsOut, { recursive: true });
    writeFileSync(path.join(agentsOut, 'speckit-overlay.orchestrator.md'), 'old');

    const result = runCli(['add-workflows', 'speckit', '--output', agentsOut, '--force'], tmpDir);

    assert.equal(result.exitCode, 0, `stderr: ${result.stderr}`);
  });

  it('should detect per-file conflicts and exit 1 without --force', () => {
    tmpDir = mkdtempSync(path.join(os.tmpdir(), 'awkit-addwf-'));
    const agentsOut = path.join(tmpDir, '.cursor', 'agents');
    mkdirSync(agentsOut, { recursive: true });
    writeFileSync(path.join(agentsOut, 'speckit-overlay.orchestrator.md'), 'old');

    const result = runCli(['add-workflows', 'speckit', '--output', agentsOut], tmpDir);

    assert.notEqual(result.exitCode, 0);
    const output = result.stdout + result.stderr;
    assert.ok(output.includes('conflict') || output.includes('Destination'));
  });

  it('should exit 1 with available list for invalid workflow name', () => {
    tmpDir = mkdtempSync(path.join(os.tmpdir(), 'awkit-addwf-'));
    const result = runCli(['add-workflows', 'nonexistent-workflow-xyz'], tmpDir);

    assert.notEqual(result.exitCode, 0);
    const output = result.stdout + result.stderr;
    assert.ok(output.includes('not found'));
    assert.ok(output.includes('speckit'));
  });

  it('should copy agent files to custom output directory with --output', () => {
    tmpDir = mkdtempSync(path.join(os.tmpdir(), 'awkit-addwf-'));
    const customOut = path.join(tmpDir, 'my-agents');
    const result = runCli(['add-workflows', 'speckit', '--output', customOut], tmpDir);

    assert.equal(result.exitCode, 0, `stderr: ${result.stderr}`);
    assert.ok(existsSync(path.join(customOut, 'speckit-overlay.orchestrator.md')));
  });
});
