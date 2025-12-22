/**
 * Capitalize the first letter of a string
 * @param {string} str - The string to capitalize
 * @returns {string} The capitalized string
 */
export function capitalize(str) {
  if (!str || typeof str !== 'string') {
    return '';
  }
  return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Convert a string to a URL-friendly slug
 * @param {string} str - The string to slugify
 * @returns {string} The slugified string
 */
export function slugify(str) {
  if (!str || typeof str !== 'string') {
    return '';
  }
  return str
    .toLowerCase()
    .trim()
    .replace(/\s+/g, '-')           // Replace spaces with hyphens
    .replace(/[^\w\-]+/g, '')       // Remove special characters
    .replace(/\-\-+/g, '-')         // Replace multiple hyphens with single hyphen
    .replace(/^-+/, '')             // Remove leading hyphens
    .replace(/-+$/, '');            // Remove trailing hyphens
}

/**
 * Truncate a string to a specified length with ellipsis
 * @param {string} str - The string to truncate
 * @param {number} length - The maximum length (including ellipsis)
 * @returns {string} The truncated string
 */
export function truncate(str, length) {
  if (!str || typeof str !== 'string') {
    return '';
  }
  if (typeof length !== 'number' || length < 0) {
    return str;
  }
  if (str.length <= length) {
    return str;
  }
  // Reserve 3 characters for the ellipsis
  const truncateAt = length > 3 ? length - 3 : length;
  return str.slice(0, truncateAt) + '...';
}
