/** A resolved filesystem path (always an absolute string). */
export type ResourcePath = string;

/** Result returned by copy operations. */
export interface CopyResult {
  copied: string[];
}

/** Shared options for all CLI commands. */
export interface CommandOptions {
  output: string;
  force: boolean;
  dryRun: boolean;
}
