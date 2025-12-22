import { describe, it, expect } from 'vitest';
import { capitalize, slugify, truncate } from '../../src/utils/strings.mjs';

describe('capitalize', () => {
  it('should capitalize the first letter of a lowercase string', () => {
    expect(capitalize('hello')).toBe('Hello');
  });

  it('should keep the first letter capitalized if already uppercase', () => {
    expect(capitalize('Hello')).toBe('Hello');
  });

  it('should capitalize only the first letter', () => {
    expect(capitalize('hello world')).toBe('Hello world');
  });

  it('should handle single character strings', () => {
    expect(capitalize('a')).toBe('A');
  });

  it('should return empty string for empty input', () => {
    expect(capitalize('')).toBe('');
  });

  it('should return empty string for null or undefined', () => {
    expect(capitalize(null)).toBe('');
    expect(capitalize(undefined)).toBe('');
  });

  it('should handle strings with numbers', () => {
    expect(capitalize('123abc')).toBe('123abc');
  });

  it('should handle strings starting with special characters', () => {
    expect(capitalize('!hello')).toBe('!hello');
  });
});

describe('slugify', () => {
  it('should convert to lowercase', () => {
    expect(slugify('Hello World')).toBe('hello-world');
  });

  it('should replace spaces with hyphens', () => {
    expect(slugify('hello world')).toBe('hello-world');
  });

  it('should replace multiple spaces with single hyphen', () => {
    expect(slugify('hello   world')).toBe('hello-world');
  });

  it('should remove special characters', () => {
    expect(slugify('hello!@#$%world')).toBe('helloworld');
  });

  it('should handle mixed case and special characters', () => {
    expect(slugify('Hello World! Welcome to 2024')).toBe('hello-world-welcome-to-2024');
  });

  it('should remove leading and trailing spaces', () => {
    expect(slugify('  hello world  ')).toBe('hello-world');
  });

  it('should handle strings with hyphens already present', () => {
    expect(slugify('hello-world')).toBe('hello-world');
  });

  it('should remove multiple consecutive hyphens', () => {
    expect(slugify('hello---world')).toBe('hello-world');
  });

  it('should handle underscores (keep them)', () => {
    expect(slugify('hello_world')).toBe('hello_world');
  });

  it('should return empty string for empty input', () => {
    expect(slugify('')).toBe('');
  });

  it('should return empty string for null or undefined', () => {
    expect(slugify(null)).toBe('');
    expect(slugify(undefined)).toBe('');
  });

  it('should handle strings with only special characters', () => {
    expect(slugify('!@#$%^&*()')).toBe('');
  });

  it('should remove leading and trailing hyphens', () => {
    expect(slugify('-hello-world-')).toBe('hello-world');
  });
});

describe('truncate', () => {
  it('should truncate string longer than specified length', () => {
    expect(truncate('Hello World', 8)).toBe('Hello...');
  });

  it('should not truncate string shorter than specified length', () => {
    expect(truncate('Hello', 10)).toBe('Hello');
  });

  it('should not truncate string equal to specified length', () => {
    expect(truncate('Hello', 5)).toBe('Hello');
  });

  it('should add ellipsis when truncating', () => {
    const result = truncate('This is a long string', 10);
    expect(result).toBe('This is...');
    expect(result.length).toBe(10);
  });

  it('should handle very short length limits', () => {
    expect(truncate('Hello World', 3)).toBe('...');
  });

  it('should handle length of 1', () => {
    expect(truncate('Hello', 1)).toBe('.');
  });

  it('should handle length of 0', () => {
    expect(truncate('Hello', 0)).toBe('');
  });

  it('should return empty string for empty input', () => {
    expect(truncate('', 10)).toBe('');
  });

  it('should return empty string for null or undefined', () => {
    expect(truncate(null, 10)).toBe('');
    expect(truncate(undefined, 10)).toBe('');
  });

  it('should return original string if length is not a number', () => {
    expect(truncate('Hello World', 'invalid')).toBe('Hello World');
  });

  it('should return original string if length is negative', () => {
    expect(truncate('Hello World', -5)).toBe('Hello World');
  });

  it('should handle long strings correctly', () => {
    const longString = 'This is a very long string that needs to be truncated';
    const result = truncate(longString, 20);
    expect(result).toBe('This is a very lo...');
    expect(result.length).toBe(20);
  });
});
