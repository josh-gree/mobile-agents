/**
 * Add two numbers
 * @param {number} a - First number
 * @param {number} b - Second number
 * @returns {number} The sum of a and b
 */
export function add(a, b) {
  return a + b;
}

/**
 * Subtract two numbers
 * @param {number} a - First number
 * @param {number} b - Second number
 * @returns {number} The difference of a and b
 */
export function subtract(a, b) {
  return a - b;
}

/**
 * Multiply two numbers
 * @param {number} a - First number
 * @param {number} b - Second number
 * @returns {number} The product of a and b
 */
export function multiply(a, b) {
  return a * b;
}

/**
 * Divide two numbers
 * @param {number} a - Numerator
 * @param {number} b - Denominator
 * @returns {number} The quotient of a divided by b
 * @throws {Error} If b is zero
 */
export function divide(a, b) {
  if (b === 0) {
    throw new Error("Cannot divide by zero");
  }
  return a / b;
}
