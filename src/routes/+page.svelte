<script lang="ts">
  let { data } = $props<{ data: { books: Array<{ position: number; display_name: string; work_id: string; testament: 'old' | 'new'; usfm_code: string }> } }>();
  const navigation = [{ label: 'Home', href: '/' }, { label: 'Bible', href: '/bible' }];
</script>

<svelte:head>
  <title>Bible Study — Read deeply. Understand clearly.</title>
  <meta name="description" content="A thoughtful space to read Scripture, explore its context, and grow through structured Bible study." />
</svelte:head>

<div class="app-shell">\n  <a class="skip-link" href="#home-content">Skip to main content</a>
  <aside class="sidebar">
    <a class="brand" href="/" aria-label="Bible Study home">
      <span class="brand-mark">✦</span>
      <span><strong>the Bible</strong><small>STUDY COMPANION</small></span>
    </a>

    <div class="side-label">WORKSPACE</div>
    <nav aria-label="Main navigation">
      {#each navigation as item}
        <a class="nav-item" href={item.href} aria-current={item.href === '/' ? 'page' : undefined}>
          <span class="nav-symbol">{item.label === 'Home' ? '⌂' : '▤'}</span>
          {item.label}
        </a>
      {/each}
    </nav>

    <div class="sidebar-bottom">
      <div class="side-label">YOUR SPACE</div>
      <a class="nav-item" href="/bible"><span class="nav-symbol">▧</span> Browse books</a>
      <div class="sidebar-note">
        <span class="note-icon">✧</span>
        <p>Small steps in the Word. A deeper understanding over time.</p>
      </div>
      <div class="profile-row">
        <div class="avatar">G</div>
        <div><strong>Guest reader</strong><small>Your study space</small></div>
        <span class="more">···</span>
      </div>
    </div>
  </aside>

  <main class="main-area" id="home-content" tabindex="-1">
    <header class="topbar">
      <div class="breadcrumb">Workspace <span>/</span> Home</div>
      <div class="top-actions">
        <a class="upgrade-button" href="/bible">Open Bible <span>↗</span></a>
      </div>
    </header>

    <div class="content">
      <section class="welcome-row">
        <div>
          <div class="eyebrow"><span class="eyebrow-dot"></span> YOUR SCRIPTURE WORKSPACE</div>
          <h1>Read deeply.<br /><em>Understand clearly.</em></h1>
          <p class="intro">A calm place to read the Bible, discover its story, and build a meaningful study habit.</p>
        </div>
        <div class="welcome-art" aria-hidden="true">
          <div class="sun"></div><div class="arch"></div><div class="book-shape"><div></div><div></div></div>
          <span class="art-star star-one">✳</span><span class="art-star star-two">✦</span>
        </div>
      </section>

      <section class="continue-card">
        <div class="continue-copy">
          <div class="eyebrow light">PICK UP WHERE YOU LEFT OFF</div>
          <h2>Begin with the beginning.</h2>
          <p>Explore the opening chapter of the Bible and discover the foundations of its grand story.</p>
          <a class="primary-button" href="/bible">Browse Genesis <span>→</span></a>
        </div>
        <div class="verse-art">
          <span class="verse-number">01</span>
          <span class="verse-word">בְּרֵאשִׁית</span>
          <span class="verse-caption">IN THE BEGINNING</span>
          <div class="verse-lines"><i></i><i></i><i></i></div>
        </div>
      </section>

      <section class="section-block">
        <div class="section-heading">
          <div><div class="eyebrow">A GOOD PLACE TO START</div><h2>Explore the Scriptures</h2></div>
          <a class="text-link" href="/bible">Browse all 66 books <span>→</span></a>
        </div>
        <div class="book-grid">
          {#each data.books.slice(0, 6) as book, i}
            <a class="book-card" href="/bible?book={book.work_id}">
              <span class="book-index">{String(i + 1).padStart(2, '0')}</span>
              <span class="book-name">{book.display_name}</span>
              <span class="book-meta">{book.testament === 'old' ? 'Old Testament' : 'New Testament'}</span>
              <span class="book-arrow">↗</span>
            </a>
          {/each}
        </div>
      </section>

      <section class="bottom-grid">
        <article class="daily-card">
          <div class="eyebrow">A MOMENT IN THE WORD</div>
          <div class="daily-quote">Read a passage. Observe its context. Follow its connections.</div>
          <div class="daily-ref">A SIMPLE STUDY RHYTHM</div>
        </article>
        <article class="progress-card">
          <div class="eyebrow">YOUR READING JOURNEY</div>
          <h3>Every chapter is a step forward.</h3>
          <p>Your reading progress and notes will live here as you build your personal study library.</p>
          <div class="progress-track"><span></span></div>
          <small>Ready when you are</small>
        </article>
      </section>

      <footer>Built for thoughtful reading and careful study. <span>Scripture first · Context always</span></footer>
    </div>
  </main>
</div>
