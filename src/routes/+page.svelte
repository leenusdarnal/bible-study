<script lang="ts">
  let activeTab = $state('Overview');
  let searchQuery = $state('');
  let showSearch = $state(false);

  const navigation = ['Home', 'Bible', 'Study', 'Explore', 'Research'];
  const books = [
    { name: 'Genesis', chapters: 50, testament: 'Old Testament' },
    { name: 'Psalms', chapters: 150, testament: 'Old Testament' },
    { name: 'Proverbs', chapters: 31, testament: 'Old Testament' },
    { name: 'Matthew', chapters: 28, testament: 'New Testament' },
    { name: 'John', chapters: 21, testament: 'New Testament' },
    { name: 'Romans', chapters: 16, testament: 'New Testament' }
  ];
</script>

<svelte:head>
  <title>Bible Study — Read deeply. Understand clearly.</title>
  <meta name="description" content="A thoughtful space to read Scripture, explore its context, and grow through structured Bible study." />
</svelte:head>

<div class="app-shell">
  <aside class="sidebar">
    <a class="brand" href="/" aria-label="Bible Study home">
      <span class="brand-mark">✦</span>
      <span><strong>the Bible</strong><small>STUDY COMPANION</small></span>
    </a>

    <div class="side-label">WORKSPACE</div>
    <nav aria-label="Main navigation">
      {#each navigation as item}
        <button class:active={activeTab === item} class="nav-item" onclick={() => activeTab = item}>
          <span class="nav-symbol">{item === 'Home' ? '⌂' : item === 'Bible' ? '▤' : item === 'Study' ? '✎' : item === 'Explore' ? '◎' : '⌕'}</span>
          {item}
        </button>
      {/each}
    </nav>

    <div class="sidebar-bottom">
      <div class="side-label">YOUR SPACE</div>
      <button class="nav-item"><span class="nav-symbol">▧</span> My Library</button>
      <button class="nav-item"><span class="nav-symbol">◷</span> Reading plans</button>
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

  <main class="main-area">
    <header class="topbar">
      <div class="breadcrumb">Workspace <span>/</span> {activeTab}</div>
      <div class="top-actions">
        <button class="icon-button" aria-label="Search" onclick={() => showSearch = !showSearch}>⌕</button>
        <button class="theme-button" aria-label="Appearance settings">◐</button>
        <button class="upgrade-button">Create your library <span>↗</span></button>
      </div>
    </header>

    {#if showSearch}
      <form class="search-panel" onsubmit={(event) => event.preventDefault()}>
        <span>⌕</span>
        <input bind:value={searchQuery} placeholder="Search a passage, person, place or topic…" autofocus />
        <button type="button" onclick={() => showSearch = false}>Esc</button>
      </form>
    {/if}

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
          <button class="primary-button" onclick={() => activeTab = 'Bible'}>Open Genesis 1 <span>→</span></button>
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
          <button class="text-link" onclick={() => activeTab = 'Bible'}>Browse all books <span>→</span></button>
        </div>
        <div class="book-grid">
          {#each books as book, i}
            <button class="book-card" onclick={() => activeTab = 'Bible'}>
              <span class="book-index">{String(i + 1).padStart(2, '0')}</span>
              <span class="book-name">{book.name}</span>
              <span class="book-meta">{book.testament} · {book.chapters} chapters</span>
              <span class="book-arrow">↗</span>
            </button>
          {/each}
        </div>
      </section>

      <section class="bottom-grid">
        <article class="daily-card">
          <div class="eyebrow">A MOMENT IN THE WORD</div>
          <div class="daily-quote">“Your word is a lamp to my feet and a light to my path.”</div>
          <div class="daily-ref">PSALM 119:105 <span>·</span> NIV</div>
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
