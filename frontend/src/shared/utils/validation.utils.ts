/**
 * SPARK — Validation Utility Functions
 * Form validation helpers used across all feature forms.
 */

/**
 * Returns an error message if the value is empty, otherwise undefined.
 */
export function required(value: unknown, fieldName = "This field"): string | undefined {
  if (value === undefined || value === null || value === "") {
    return `${fieldName} is required`;
  }
  return undefined;
}

/**
 * Returns an error message if the string is shorter than minLength.
 */
export function minLength(
  value: string,
  min: number,
  fieldName = "This field"
): string | undefined {
  if (value.length < min) {
    return `${fieldName} must be at least ${min} characters`;
  }
  return undefined;
}

/**
 * Returns an error message if the string exceeds maxLength.
 */
export function maxLength(
  value: string,
  max: number,
  fieldName = "This field"
): string | undefined {
  if (value.length > max) {
    return `${fieldName} must be at most ${max} characters`;
  }
  return undefined;
}

/**
 * Returns an error message if value is not a valid future date.
 */
export function futureDate(value: string, fieldName = "Deadline"): string | undefined {
  const date = new Date(value);
  if (isNaN(date.getTime())) {
    return `${fieldName} must be a valid date`;
  }
  if (date <= new Date()) {
    return `${fieldName} must be in the future`;
  }
  return undefined;
}

/**
 * Returns an error message if value is not a positive number.
 */
export function positiveNumber(
  value: number,
  fieldName = "This field"
): string | undefined {
  if (isNaN(value) || value <= 0) {
    return `${fieldName} must be a positive number`;
  }
  return undefined;
}

/**
 * Compose multiple validators — returns first error found.
 */
export function compose(
  ...validators: Array<string | undefined>
): string | undefined {
  return validators.find((v) => v !== undefined);
}