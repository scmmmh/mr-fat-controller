/**
 * Generate a list covering a range of numbers.
 *
 * @param start The first number to include.
 * @param end All included numbers will be less than this number.
 * @param step The step distance between numbers.
 * @returns A list of numbers
 */
export function range(start: number, end: number, step: number) {
  const buffer: number[] = [];
  for (let idx = start; idx <= end; idx = idx + step) {
    buffer.push(Math.floor(idx));
  }
  return buffer;
}
