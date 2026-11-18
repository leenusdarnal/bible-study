<script lang="ts">
  import { filterCanonBooks, type CanonBook } from '$lib/bible-catalogue';

  let { data } = $props<{
    data: { books: CanonBook[]; initialBook: string; databaseAvailable: boolean };
  }>();

  let search = $state('');
  let testament = $state<'all' | 'old' | 'new'>('all');
  let selectedId = $state(data.initialBook);

  const selectedBook = $derived(data.books.find((book) => book.work_id === selectedId));
  const filteredBooks = $derived(filterCanonBooks(data.books, search, testament));
</script>

<svelte:head>
  <title>Browse the Bible | Bible Study</title>
  <meta name="description" content="Browse the 66 books of the Protestant Bible and open the Scripture reader." />
</svelte:head>

<div class="library-page">
  <a class="skip-link" href="#reader-content">Skip to selected book</a>
  <header class="reader-header">
    <a class="back-link" href="/">← Home</a>
    <div class="header-title"><span class="eyebrow">SCRIPTURE LIBRARY</span><h1>Browse the Bible</h1></div>
    <span class="canon-label">Protestant canon · 66 books</span>
  </header>

  {#if !data.databaseAvailable}
    <div class="notice" role="status">
      <strong>Catalogue connection unavailable</strong>
      <p>The Bible catalogue could not be loaded. Please try again later.</p>
    </div>
  {:else}
    <div class="library-layout">
      <aside class="book-browser" aria-label="Bible book catalogue">
        <div class="browser-heading">
          <div><span class="eyebrow">THE CANON</span><h2>Books</h2></div>
          <span class="count">{data.books.length}</span>
        </div>

        <label class="search-label" for="book-search">Find a book</label>
        <input id="book-search" class="book-search" type="search" bind:value={search} placeholder="Search books…" />

        <div class="filters" aria-label="Filter books by testament">
          <button class:chosen={testament === 'all'} aria-pressed={testament === 'all'} onclick={() => testament = 'all'}>All</button>
          <button class:chosen={testament === 'old'} aria-pressed={testament === 'old'} onclick={() => testament = 'old'}>Old</button>
          <button class:chosen={testament === 'new'} aria-pressed={testament === 'new'} onclick={() => testament = 'new'}>New</button>
        </div>

        <div class="book-list">
          {#each filteredBooks as book}
            <button
              class="book-option"
              class:selected={selectedId === book.work_id}
              aria-pressed={selectedId === book.work_id}
              onclick={() => selectedId = book.work_id}
            >
              <span class="book-order">{String(book.position).padStart(2, '0')}</span>
              <span class="book-option-name">{book.display_name}</span>
              <span class="book-testament">{book.testament === 'old' ? 'OT' : 'NT'}</span>
            </button>
          {/each}
          {#if filteredBooks.length === 0}
            <p class="empty-result">No books match that search.</p>
          {/if}
        </div>
      </aside>

      <main class="reader-panel" id="reader-content" tabindex="-1">
        {#if selectedBook}
          <div class="reader-kicker">{selectedBook.testament === 'old' ? 'OLD TESTAMENT' : 'NEW TESTAMENT'} <span>·</span> BOOK {selectedBook.position}</div>
          <h2>{selectedBook.display_name}</h2>
          <p class="book-intro">You are viewing the catalogue entry for {selectedBook.display_name}. Choose a chapter when verified chapter data is available.</p>

          <div class="reader-divider"></div>

          {#if selectedBook.chapter_count > 0}
            <div class="chapter-summary">
              <span class="eyebrow">VERIFIED CHAPTER STRUCTURE</span>
              <strong>{selectedBook.chapter_count} chapters</strong>
              <p>Chapter navigation can be enabled once the approved versification scheme is connected to the reader.</p>
            </div>
          {:else}
            <div class="empty-reader">
              <div class="empty-icon" aria-hidden="true">✧</div>
              <span class="eyebrow">READER CONTENT IN PREPARATION</span>
              <h3>Your reading space is being prepared.</h3>
              <p>The book catalogue is connected, but verified chapter structure and licensed translation text have not yet been published. No chapter or verse wording is being fabricated.</p>
              <div class="reader-checks">
                <div><span class="check-dot"></span><span>66-book canon connected</span></div>
                <div><span class="pending-dot"></span><span>Verified chapter data pending</span></div>
                <div><span class="pending-dot"></span><span>Translation publication pending</span></div>
              </div>
            </div>
          {/if}
        {:else}
          <div class="empty-reader"><h3>Select a book</h3><p>Choose a title from the catalogue to view its reader status.</p></div>
        {/if}
      </main>
    </div>
  {/if}

  <footer class="library-footer">Scripture first · Context always <span>Translation text will appear only after rights and source review.</span></footer>
</div>

<style>
  .skip-link{position:absolute;left:12px;top:-60px;background:#344d3b;color:#fff;padding:10px 14px;border-radius:6px;z-index:10}.skip-link:focus{top:12px}
  .library-page{min-height:100vh;background:#f7f6f1;color:#29372d;padding:0 clamp(18px,5vw,76px);font-family:Arial,Helvetica,sans-serif}
  .reader-header{min-height:145px;display:flex;align-items:center;justify-content:space-between;gap:24px;border-bottom:1px solid #e7e5dc}
  .back-link{color:#62725f;text-decoration:none;font-size:12px;white-space:nowrap}
  .header-title{text-align:center}.eyebrow{display:block;font-size:9px;font-weight:700;letter-spacing:1.7px;color:#92988b}
  h1,h2,h3{font-family:Georgia,'Times New Roman',serif;font-weight:400}
  h1{font-size:clamp(30px,4vw,43px);margin:8px 0 0}
  .canon-label{font-size:10px;color:#7f897d;white-space:nowrap}
  .library-layout{display:grid;grid-template-columns:minmax(250px,340px) minmax(0,1fr);gap:22px;max-width:1180px;margin:30px auto 0;align-items:start}
  .book-browser,.reader-panel{background:#fbfaf6;border:1px solid #e7e5dc;border-radius:12px}
  .book-browser{padding:22px;max-height:calc(100vh - 205px);overflow:auto}
  .browser-heading{display:flex;align-items:center;justify-content:space-between;margin-bottom:18px}
  .browser-heading h2{font-size:25px;margin:5px 0 0}
  .count{font-size:11px;color:#687967;background:#e9ede5;padding:6px 9px;border-radius:20px}
  .search-label{display:block;font-size:10px;font-weight:700;color:#687568;margin-bottom:7px}
  .book-search{width:100%;border:1px solid #dedfd5;border-radius:7px;background:#fff;padding:11px 12px;font:inherit;font-size:12px;color:#29372d}
  .book-search:focus-visible,.filters button:focus-visible,.book-option:focus-visible,.back-link:focus-visible{outline:3px solid #9b8659;outline-offset:2px}
  .filters{display:flex;gap:6px;margin:13px 0 15px}
  .filters button{border:1px solid #e2e3da;background:#f7f6f1;border-radius:6px;padding:7px 12px;font-size:10px;color:#737d70}
  .filters button.chosen{background:#e4e9df;border-color:#cbd5c6;color:#344d3b;font-weight:700}
  .book-list{display:grid;gap:3px}
  .book-option{display:flex;align-items:center;gap:11px;width:100%;text-align:left;border:0;background:transparent;border-radius:6px;padding:9px 8px;color:#3d493f}
  .book-option:hover{background:#f2f2eb}.book-option.selected{background:#e8ede4;color:#304b37}
  .book-order{font-size:9px;color:#a3a492;width:19px}.book-option-name{font-family:Georgia,'Times New Roman',serif;font-size:14px;flex:1}
  .book-testament{font-size:8px;color:#9a9d91;letter-spacing:.7px}
  .empty-result{font-size:12px;color:#858b80;padding:8px}
  .reader-panel{min-height:590px;padding:clamp(25px,5vw,58px);background:linear-gradient(145deg,#fbfaf6,#f5f4ed)}
  .reader-kicker{font-size:9px;font-weight:700;letter-spacing:1.7px;color:#92988b}.reader-kicker span{padding:0 5px}
  .reader-panel>h2{font-size:clamp(38px,5vw,58px);margin:12px 0;color:#344638}
  .book-intro{font-size:13px;line-height:1.8;color:#7c857a;max-width:520px;margin:0}
  .reader-divider{height:1px;background:#e5e4d9;margin:35px 0}
  .empty-reader{max-width:520px;padding:25px 0}
  .empty-icon{width:43px;height:43px;display:grid;place-items:center;background:#e9ede4;color:#73856d;border-radius:50%;font-size:21px;margin-bottom:22px}
  .empty-reader h3{font-size:27px;margin:10px 0;color:#344638}
  .empty-reader p,.chapter-summary p{font-size:12px;line-height:1.85;color:#7e877b;max-width:490px}
  .reader-checks{display:grid;gap:12px;margin-top:26px;font-size:11px;color:#647263}
  .reader-checks>div{display:flex;align-items:center;gap:9px}.check-dot,.pending-dot{width:7px;height:7px;border-radius:50%;background:#71866d}.pending-dot{background:#c1ad7e}
  .chapter-summary strong{display:block;font:26px Georgia,serif;margin-top:12px;color:#3a4b3b}
  .notice{max-width:700px;margin:50px auto;background:#fbfaf6;padding:25px;border:1px solid #e7e5dc;border-radius:10px}.notice p{font-size:12px;color:#7e877b}
  .library-footer{max-width:1180px;margin:35px auto 0;padding:18px 0;border-top:1px solid #e7e5dc;display:flex;justify-content:space-between;gap:15px;font-size:10px;color:#758071}.library-footer span{color:#9a9e93;text-align:right}
  @media(max-width:760px){.reader-header{min-height:125px;flex-wrap:wrap;justify-content:space-between;padding:18px 0}.header-title{order:3;width:100%;text-align:left}.library-layout{grid-template-columns:1fr;margin-top:18px}.book-browser{max-height:420px}.reader-panel{min-height:420px}.library-footer{flex-direction:column}.library-footer span{text-align:left}}
  @media(prefers-reduced-motion:reduce){*,*::before,*::after{scroll-behavior:auto!important;transition:none!important}}
</style>
