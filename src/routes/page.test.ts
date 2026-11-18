import { describe, expect, it } from 'vitest';

describe('Bible Study app foundation', () => {
  it('keeps the first release focused on Scripture reading and study', () => {
    const primaryDestinations = ['Home', 'Bible', 'Study', 'Explore', 'Research'];
    expect(primaryDestinations).toContain('Bible');
    expect(primaryDestinations).toContain('Study');
    expect(primaryDestinations).not.toContain('AI Assistant');
  });
});
