import type { PageServerLoad } from './$types';

type CanonBook = {
  position: number;
  display_name: string;
  work_id: string;
  testament: 'old' | 'new';
  usfm_code: string;
};

export const load: PageServerLoad = async ({ platform }) => {
  if (!platform?.env?.DB) return { books: [] as CanonBook[] };

  const { results } = await platform.env.DB.prepare(`
    SELECT
      cb.position,
      cb.display_name,
      sw.id AS work_id,
      sw.testament,
      sw.usfm_code
    FROM canon_books cb
    INNER JOIN scriptural_works sw ON sw.id = cb.work_id
    WHERE cb.canon_id = ? AND cb.is_included = 1
    ORDER BY cb.position ASC
  `).bind('canon-protestant-66').all<CanonBook>();

  return { books: results };
};
