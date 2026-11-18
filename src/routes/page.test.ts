import { describe, expect, it } from 'vitest';
import { filterCanonBooks, resolveInitialBook, type CanonBook } from '$lib/bible-catalogue';

const books: CanonBook[] = [
  { position: 1, display_name: 'Genesis', work_id: 'GEN', testament: 'old', usfm_code: 'GEN', chapter_count: 0 },
  { position: 2, display_name: 'Exodus', work_id: 'EXO', testament: 'old', usfm_code: 'EXO', chapter_count: 0 },
  { position: 40, display_name: 'Matthew', work_id: 'MAT', testament: 'new', usfm_code: 'MAT', chapter_count: 0 }
];

describe('Bible catalogue helpers', () => {
  it('filters by book name without case sensitivity', () => {
    expect(filterCanonBooks(books, 'gen', 'all').map((book) => book.work_id)).toEqual(['GEN']);
  });

  it('filters by testament', () => {
    expect(filterCanonBooks(books, '', 'new').map((book) => book.work_id)).toEqual(['MAT']);
  });

  it('combines name and testament filters', () => {
    expect(filterCanonBooks(books, 'e', 'old').map((book) => book.work_id)).toEqual(['GEN', 'EXO']);
  });

  it('uses a valid requested book and safely falls back to the first book', () => {
    expect(resolveInitialBook(books, 'MAT')).toBe('MAT');
    expect(resolveInitialBook(books, 'UNKNOWN')).toBe('GEN');
    expect(resolveInitialBook([], null)).toBe('');
  });
});
