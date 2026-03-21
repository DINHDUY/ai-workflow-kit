import { mkdirSync, readdirSync, copyFileSync } from 'node:fs';
import * as path from 'node:path';

/** Directory names excluded from recursive copy operations. */
export const SKIP_DIRS = new Set([
  '__pycache__',
  '.git',
  'node_modules',
  'dist',
  '.turbo',
]);

/** Recursively copy a directory tree, returning absolute paths of written files. */
export function copyTree(src: string, dst: string): string[] {
  mkdirSync(dst, { recursive: true });
  const copied: string[] = [];

  for (const entry of readdirSync(src, { withFileTypes: true })) {
    if (SKIP_DIRS.has(entry.name)) continue;
    const srcPath = path.join(src, entry.name);
    const dstPath = path.join(dst, entry.name);
    if (entry.isFile()) {
      copyFileSync(srcPath, dstPath);
      copied.push(path.resolve(dstPath));
    } else if (entry.isDirectory()) {
      copied.push(...copyTree(srcPath, dstPath));
    }
  }
  return copied;
}

/** Copy a single file, creating parent directories as needed. Returns the absolute destination path. */
export function copyFile(src: string, dst: string): string {
  mkdirSync(path.dirname(dst), { recursive: true });
  copyFileSync(src, dst);
  return path.resolve(dst);
}
