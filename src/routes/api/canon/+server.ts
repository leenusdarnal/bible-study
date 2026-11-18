import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

type CanonBook = {
  position: number;
  display_name: string;
  work_id: string;
  testament: 'old' | 'new';
  usfm_code: string;
};

export const GET: RequestHandler = async ({ platform }) => {
  if (!platform?.env?.DB) {
    return json({ error: 'Scripture catalogue is not configured.' }, { status: 503 });
  }

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
  `).all<CanonBook>('canon-protestant-66');

  return json({
    canon: 'protestant-66',
    total: results.length,
    books: results
  }, {
    headers: {
      'cache-control': 'public, max-age=300, stale-while-revalidate=3600'
    }
  });
};
