import type { PageServerLoad } from './$types';\nimport { resolveInitialBook, type CanonBook } from '$lib/bible-catalogue';



export const load: PageServerLoad = async ({ platform, url }) => {
  if (!platform?.env?.DB) {
    return { books: [] as CanonBook[], initialBook: '', databaseAvailable: false };
  }

  const { results } = await platform.env.DB.prepare(`
    SELECT
      cb.position,
      cb.display_name,
      sw.id AS work_id,
      sw.testament,
      sw.usfm_code,
      COUNT(DISTINCT CASE WHEN vs.status = 'verified' THEN sc.id END) AS chapter_count
    FROM canon_books cb
    INNER JOIN scriptural_works sw ON sw.id = cb.work_id
    LEFT JOIN scheme_chapters sc ON sc.work_id = sw.id
    LEFT JOIN versification_schemes vs
      ON vs.id = sc.scheme_id AND vs.status = 'verified'
    WHERE cb.canon_id = ? AND cb.is_included = 1
    GROUP BY cb.position, cb.display_name, sw.id, sw.testament, sw.usfm_code
    ORDER BY cb.position ASC
  `).bind('canon-protestant-66').all<CanonBook>();

  const initialBook = resolveInitialBook(results, url.searchParams.get('book'));
