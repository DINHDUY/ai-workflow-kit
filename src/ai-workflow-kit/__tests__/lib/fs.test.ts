import { describe, it, after } from 'node:test';
import assert from 'node:assert/strict';
import { mkdirSync, writeFileSync, readFileSync, existsSync, mkdtempSync, rmSync } from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { copyTree, copyFile, SKIP_DIRS } from '../../lib/fs.js';

describe('SKIP_DIRS', () => {
  it('should contain expected directory names', () => {
    assert.ok(SKIP_DIRS.has('__pycache__'));
    assert.ok(SKIP_DIRS.has('.git'));
    assert.ok(SKIP_DIRS.has('node_modules'));
    assert.ok(SKIP_DIRS.has('dist'));
    assert.ok(SKIP_DIRS.has('.turbo'));
    assert.equal(SKIP_DIRS.size, 5);
  });
});

describe('copyTree', () => {
  let tmpDir: string;

  after(() => {
    if (tmpDir) rmSync(tmpDir, { recursive: true, force: true });
  });

  it('should recursively copy a directory tree', () => {
    tmpDir = mkdtempSync(path.join(os.tmpdir(), 'awkit-fs-'));
    const src = path.join(tmpDir, 'src');
    const dst = path.join(tmpDir, 'dst');

    mkdirSync(path.join(src, 'sub'), { recursive: true });
    writeFileSync(path.join(src, 'a.txt'), 'hello');
    writeFileSync(path.join(src, 'sub', 'b.txt'), 'world');

    const result = copyTree(src, dst);

    assert.equal(result.length, 2);
    assert.ok(existsSync(path.join(dst, 'a.txt')));
    assert.ok(existsSync(path.join(dst, 'sub', 'b.txt')));
    assert.equal(readFileSync(path.join(dst, 'a.txt'), 'utf8'), 'hello');
    assert.equal(readFileSync(path.join(dst, 'sub', 'b.txt'), 'utf8'), 'world');
  });

  it('should skip entries in SKIP_DIRS', () => {
    tmpDir = mkdtempSync(path.join(os.tmpdir(), 'awkit-fs-'));
    const src = path.join(tmpDir, 'src');
    const dst = path.join(tmpDir, 'dst');

    mkdirSync(path.join(src, 'node_modules'), { recursive: true });
    mkdirSync(path.join(src, '__pycache__'), { recursive: true });
    mkdirSync(path.join(src, '.git'), { recursive: true });
    mkdirSync(path.join(src, 'keep'), { recursive: true });
    writeFileSync(path.join(src, 'node_modules', 'pkg.json'), '{}');
    writeFileSync(path.join(src, '__pycache__', 'cache.pyc'), '');
    writeFileSync(path.join(src, '.git', 'HEAD'), '');
    writeFileSync(path.join(src, 'keep', 'ok.txt'), 'ok');

    const result = copyTree(src, dst);

    assert.equal(result.length, 1);
    assert.ok(existsSync(path.join(dst, 'keep', 'ok.txt')));
    assert.ok(!existsSync(path.join(dst, 'node_modules')));
    assert.ok(!existsSync(path.join(dst, '__pycache__')));
    assert.ok(!existsSync(path.join(dst, '.git')));
  });

  it('should create destination directories as needed', () => {
    tmpDir = mkdtempSync(path.join(os.tmpdir(), 'awkit-fs-'));
    const src = path.join(tmpDir, 'src');
    const dst = path.join(tmpDir, 'deep', 'nested', 'dst');

    mkdirSync(src, { recursive: true });
    writeFileSync(path.join(src, 'file.txt'), 'data');

    const result = copyTree(src, dst);

    assert.equal(result.length, 1);
    assert.ok(existsSync(path.join(dst, 'file.txt')));
  });

  it('should handle empty source directory', () => {
    tmpDir = mkdtempSync(path.join(os.tmpdir(), 'awkit-fs-'));
    const src = path.join(tmpDir, 'empty');
    const dst = path.join(tmpDir, 'dst');

    mkdirSync(src, { recursive: true });

    const result = copyTree(src, dst);

    assert.equal(result.length, 0);
    assert.ok(existsSync(dst));
  });
});

describe('copyFile', () => {
  let tmpDir: string;

  after(() => {
    if (tmpDir) rmSync(tmpDir, { recursive: true, force: true });
  });

  it('should copy a single file', () => {
    tmpDir = mkdtempSync(path.join(os.tmpdir(), 'awkit-fs-'));
    const src = path.join(tmpDir, 'source.txt');
    const dst = path.join(tmpDir, 'dest.txt');

    writeFileSync(src, 'content');

    const result = copyFile(src, dst);

    assert.ok(existsSync(dst));
    assert.equal(readFileSync(dst, 'utf8'), 'content');
    assert.equal(result, path.resolve(dst));
  });

  it('should create parent directories if missing', () => {
    tmpDir = mkdtempSync(path.join(os.tmpdir(), 'awkit-fs-'));
    const src = path.join(tmpDir, 'source.txt');
    const dst = path.join(tmpDir, 'a', 'b', 'c', 'dest.txt');

    writeFileSync(src, 'nested');

    const result = copyFile(src, dst);

    assert.ok(existsSync(dst));
    assert.equal(readFileSync(dst, 'utf8'), 'nested');
    assert.equal(result, path.resolve(dst));
  });
});
