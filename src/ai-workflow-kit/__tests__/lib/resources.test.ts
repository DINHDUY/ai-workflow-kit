import { describe, it } from 'node:test';
import assert from 'node:assert/strict';
import {
  getResourceDir,
  getAvailableSkills,
  getAvailableCommands,
  getAvailableWorkflows,
} from '../../lib/resources.js';

describe('getResourceDir', () => {
  it('should return path to skills directory', () => {
    const dir = getResourceDir('skills');
    assert.ok(dir.endsWith('skills') || dir.includes('skills'));
    assert.ok(typeof dir === 'string');
  });

  it('should return path to commands directory', () => {
    const dir = getResourceDir('commands');
    assert.ok(dir.includes('commands'));
  });

  it('should return path to workflows directory', () => {
    const dir = getResourceDir('workflows');
    assert.ok(dir.includes('workflows'));
  });

  it('should throw descriptive error for missing resource directory', () => {
    assert.throws(
      () => getResourceDir('nonexistent-resource-xyz'),
      (err: unknown) => {
        assert.ok(err instanceof Error);
        assert.ok(err.message.includes('nonexistent-resource-xyz'));
        assert.ok(err.message.includes('not found'));
        return true;
      }
    );
  });
});

describe('getAvailableSkills', () => {
  it('should return sorted array of skill directory names', () => {
    const skills = getAvailableSkills();
    assert.ok(Array.isArray(skills));
    assert.ok(skills.length > 0);
    const sorted = [...skills].sort();
    assert.deepEqual(skills, sorted);
  });

  it('should include known skill names', () => {
    const skills = getAvailableSkills();
    assert.ok(skills.includes('template'));
  });
});

describe('getAvailableCommands', () => {
  it('should return sorted array of command directory names', () => {
    const commands = getAvailableCommands();
    assert.ok(Array.isArray(commands));
    assert.ok(commands.length > 0);
    const sorted = [...commands].sort();
    assert.deepEqual(commands, sorted);
  });

  it('should include known command names', () => {
    const commands = getAvailableCommands();
    assert.ok(commands.includes('abc'));
  });
});

describe('getAvailableWorkflows', () => {
  it('should return sorted array of workflow directory names', () => {
    const workflows = getAvailableWorkflows();
    assert.ok(Array.isArray(workflows));
    assert.ok(workflows.length > 0);
    const sorted = [...workflows].sort();
    assert.deepEqual(workflows, sorted);
  });

  it('should include known workflow names', () => {
    const workflows = getAvailableWorkflows();
    assert.ok(workflows.includes('speckit'));
  });
});
