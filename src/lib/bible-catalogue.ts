export type CanonBook = {
  position: number;
  display_name: string;
  work_id: string;
  testament: 'old' | 'new';
  usfm_code: string;
  chapter_count: number;
};

export type TestamentFilter = 'all' | 'old' | 'new';

export function filterCanonBooks(
  books: CanonBook[],
  search: string,
  testament: TestamentFilter
): CanonBook[] {
  const term = search.trim().toLowerCase();
  return books.filter((book) => {
    const matchesSearch = book.display_name.toLowerCase().includes(term);
    const matchesTestament = testament === 'all' || book.testament === testament;
    return matchesSearch && matchesTestament;
  });
}

export function resolveInitialBook(books: CanonBook[], requestedBook: string | null): string {
  if (requestedBook && books.some((book) => book.work_id === requestedBook)) return requestedBook;
  return books[0]?.work_id ?? '';
}
