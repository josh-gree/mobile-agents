import { describe, it, expect } from "vitest";
import { add, subtract, multiply, divide } from "../src/calculator.mjs";

describe("add", () => {
  it("adds two positive numbers", () => {
    expect(add(2, 3)).toBe(5);
  });

  it("adds a positive and negative number", () => {
    expect(add(5, -3)).toBe(2);
  });

  it("adds two negative numbers", () => {
    expect(add(-5, -3)).toBe(-8);
  });

  it("adds zero to a number", () => {
    expect(add(10, 0)).toBe(10);
  });

  it("adds decimal numbers", () => {
    expect(add(1.5, 2.3)).toBeCloseTo(3.8);
  });
});

describe("subtract", () => {
  it("subtracts two positive numbers", () => {
    expect(subtract(5, 3)).toBe(2);
  });

  it("subtracts a larger number from a smaller number", () => {
    expect(subtract(3, 5)).toBe(-2);
  });

  it("subtracts a negative number", () => {
    expect(subtract(5, -3)).toBe(8);
  });

  it("subtracts zero from a number", () => {
    expect(subtract(10, 0)).toBe(10);
  });

  it("subtracts decimal numbers", () => {
    expect(subtract(5.7, 2.3)).toBeCloseTo(3.4);
  });
});

describe("multiply", () => {
  it("multiplies two positive numbers", () => {
    expect(multiply(4, 5)).toBe(20);
  });

  it("multiplies a positive and negative number", () => {
    expect(multiply(4, -5)).toBe(-20);
  });

  it("multiplies two negative numbers", () => {
    expect(multiply(-4, -5)).toBe(20);
  });

  it("multiplies by zero", () => {
    expect(multiply(10, 0)).toBe(0);
  });

  it("multiplies decimal numbers", () => {
    expect(multiply(2.5, 4)).toBe(10);
  });
});

describe("divide", () => {
  it("divides two positive numbers", () => {
    expect(divide(10, 2)).toBe(5);
  });

  it("divides a positive by a negative number", () => {
    expect(divide(10, -2)).toBe(-5);
  });

  it("divides two negative numbers", () => {
    expect(divide(-10, -2)).toBe(5);
  });

  it("divides decimal numbers", () => {
    expect(divide(7.5, 2.5)).toBe(3);
  });

  it("divides resulting in a decimal", () => {
    expect(divide(5, 2)).toBe(2.5);
  });

  it("throws an error when dividing by zero", () => {
    expect(() => divide(10, 0)).toThrow("Cannot divide by zero");
  });

  it("throws an error when dividing zero by zero", () => {
    expect(() => divide(0, 0)).toThrow("Cannot divide by zero");
  });
});
