import { useMemo, useState } from 'react';
import {
  ArrowDown,
  ArrowUpRight,
  BookOpenText,
  Building2,
  ExternalLink,
  FileCheck2,
  FileText,
  Landmark,
  Search,
  ShieldCheck,
} from 'lucide-react';
import { categories, checkedAt, records, type RecordCategory } from './data/records';

const categoryIcon: Record<RecordCategory, typeof FileText> = {
  Services: BookOpenText,
  'Local policies': FileCheck2,
  Offices: Building2,
  Procurement: Landmark,
};

const categoryDescription: Record<RecordCategory, string> = {
  Services: 'Service requirements and online service links',
  'Local policies': 'Ordinances and executive issuances',
  Offices: 'Municipal departments and the Sangguniang Bayan',
  Procurement: 'Bidding documents and public records',
};

function App() {
  const [query, setQuery] = useState('');
  const [activeCategory, setActiveCategory] = useState<(typeof categories)[number]>(
    'All records',
  );

  const filteredRecords = useMemo(() => {
    const normalizedQuery = query.trim().toLowerCase();
    return records.filter(record => {
      const matchesCategory =
        activeCategory === 'All records' || record.category === activeCategory;
      const searchable = [
        record.title,
        record.category,
        record.description,
        record.publisher,
        record.scope,
      ]
        .join(' ')
        .toLowerCase();
      return matchesCategory && (!normalizedQuery || searchable.includes(normalizedQuery));
    });
  }, [activeCategory, query]);

  const selectCategory = (category: RecordCategory | 'All records') => {
    setActiveCategory(category);
    document.getElementById('records')?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <>
      <a className="skip-link" href="#main-content">Skip to main content</a>

      <div className="demo-notice">
        <span className="notice-label">DEMO</span>
        <span>Better Concepcion is an independent community prototype.</span>
        <a href="#about">Learn about this project <ArrowUpRight size={13} aria-hidden="true" /></a>
      </div>

      <div className="utility-bar">
        <span>CONCEPCION · TARLAC · CENTRAL LUZON</span>
        <div>
          <a href="#records">Public records</a>
          <span aria-hidden="true">|</span>
          <a href="#about">About</a>
          <span aria-hidden="true">|</span>
          <a href="https://github.com/aaronher1030-glitch/bettergovtarlacph" target="_blank" rel="noreferrer">GitHub</a>
        </div>
      </div>

      <header className="site-header">
        <a className="brand" href="#top" aria-label="Better Concepcion home">
          <span className="brand-copy">
            <strong>BETTER<span>CONCEPCION</span></strong>
            <small>PUBLIC INFORMATION GUIDE</small>
          </span>
        </a>
        <a className="official-link" href="https://concepciontarlac.org/" target="_blank" rel="noreferrer">
          Official municipal website <ExternalLink size={15} aria-hidden="true" />
        </a>
      </header>

      <nav className="primary-nav" aria-label="Main navigation">
        <a className="nav-current" href="#top">Home</a>
        <a href="#categories">Services &amp; records</a>
        <a href="#records">Transparency</a>
        <a href="#about">About this demo</a>
      </nav>

      <main id="main-content">
        <section className="hero" id="top" aria-labelledby="hero-title">
          <div className="hero-inner">
            <div className="hero-copy">
              <p className="eyebrow">A COMMUNITY GUIDE TO LOCAL INFORMATION</p>
              <h1 id="hero-title">Find Concepcion’s public information.</h1>
              <p className="hero-description">
                Search municipal services, offices, ordinances, and public documents. Then follow each link to its original source.
              </p>
              <form
                className="search-form"
                role="search"
                onSubmit={event => {
                  event.preventDefault();
                  document.getElementById('records')?.scrollIntoView({ behavior: 'smooth' });
                }}
              >
                <Search className="search-icon" size={21} aria-hidden="true" />
                <label className="visually-hidden" htmlFor="record-search">Search public information</label>
                <input
                  id="record-search"
                  type="search"
                  placeholder="Search services, offices, or records"
                  value={query}
                  onChange={event => setQuery(event.target.value)}
                />
                <button type="submit" className="search-button">Search</button>
              </form>
              <div className="popular-searches" aria-label="Popular topics">
                <span>Popular:</span>
                <button type="button" onClick={() => { setQuery('charter'); selectCategory('All records'); }}>Citizen’s Charter</button>
                <button type="button" onClick={() => { setQuery(''); selectCategory('Local policies'); }}>Ordinances</button>
                <button type="button" onClick={() => { setQuery(''); selectCategory('Procurement'); }}>Bidding documents</button>
              </div>
            </div>

            <aside className="quick-panel" aria-label="Popular information categories">
              <div className="quick-panel-heading">
                <span className="eyebrow">START HERE</span>
                <h2>Browse by topic</h2>
              </div>
              <div className="quick-grid">
                {(['Services', 'Local policies', 'Offices', 'Procurement'] as RecordCategory[]).map(category => {
                  const Icon = categoryIcon[category];
                  return (
                    <button className="quick-link" type="button" key={category} onClick={() => selectCategory(category)}>
                      <span className="quick-icon"><Icon size={19} aria-hidden="true" /></span>
                      <span>{category}</span>
                    </button>
                  );
                })}
              </div>
              <button className="quick-all" type="button" onClick={() => selectCategory('All records')}>
                View all public sources <ArrowUpRight size={16} aria-hidden="true" />
              </button>
            </aside>
          </div>
          <a className="scroll-cue" href="#categories">Explore the directory <ArrowDown size={15} aria-hidden="true" /></a>
        </section>

        <section className="category-section" id="categories" aria-labelledby="categories-title">
          <div className="section-heading">
            <div>
              <p className="eyebrow eyebrow-blue">SERVICES &amp; RECORDS</p>
              <h2 id="categories-title">Start with what you need</h2>
            </div>
            <p className="section-description">Choose a topic to see the public sources currently listed in this demo.</p>
          </div>
          <div className="category-grid">
            {(['Services', 'Local policies', 'Offices', 'Procurement'] as RecordCategory[]).map(category => {
              const Icon = categoryIcon[category];
              const count = records.filter(record => record.category === category).length;
              return (
                <button className="category-card" type="button" key={category} onClick={() => selectCategory(category)}>
                  <span className="category-icon"><Icon size={21} aria-hidden="true" /></span>
                  <span className="category-title">{category}</span>
                  <span className="category-description">{categoryDescription[category]}</span>
                  <span className="category-bottom"><span>{count} {count === 1 ? 'source' : 'sources'}</span><ArrowUpRight size={16} aria-hidden="true" /></span>
                </button>
              );
            })}
          </div>
        </section>

        <section className="records-section" id="records" aria-labelledby="records-title">
          <div className="section-heading records-heading">
            <div>
              <p className="eyebrow eyebrow-blue">SOURCE DIRECTORY</p>
              <h2 id="records-title">Public information directory</h2>
              <p className="section-description">Each result points to the publisher’s page or document. This is a selected list, not a complete archive.</p>
            </div>
            <p className="checked-summary">Links checked <strong>{checkedAt}</strong></p>
          </div>

          <div className="filter-row" role="group" aria-label="Filter records by topic">
            {categories.map(category => (
              <button
                key={category}
                className={`filter-chip ${activeCategory === category ? 'is-active' : ''}`}
                aria-pressed={activeCategory === category}
                onClick={() => setActiveCategory(category)}
                type="button"
              >
                {category}
              </button>
            ))}
          </div>

          <p className="result-count" aria-live="polite">
            {filteredRecords.length} {filteredRecords.length === 1 ? 'source' : 'sources'}
            {query.trim() ? ` matching “${query.trim()}”` : ''}
          </p>

          {filteredRecords.length > 0 ? (
            <div className="record-list">
              {filteredRecords.map(record => {
                const Icon = categoryIcon[record.category];
                return (
                  <article className="record-row" key={record.id}>
                    <div className="record-icon" aria-hidden="true"><Icon size={20} strokeWidth={1.8} /></div>
                    <div className="record-main">
                      <div className="record-meta"><span>{record.category}</span><span className="meta-separator">·</span><span>{record.scope}</span></div>
                      <h3><a href={record.sourceUrl} target="_blank" rel="noreferrer">{record.title}</a></h3>
                      <p>{record.description}</p>
                      <div className="source-details">
                        <span>{record.publisher}</span>
                        {record.sourceDate && <span>Source date: {record.sourceDate}</span>}
                        <span>Checked {checkedAt}</span>
                      </div>
                      {record.note && <p className="record-note">Note: {record.note}</p>}
                    </div>
                    <a className="record-action" href={record.sourceUrl} target="_blank" rel="noreferrer" aria-label={`Open original source: ${record.title}`}>
                      <ArrowUpRight size={20} aria-hidden="true" />
                    </a>
                  </article>
                );
              })}
            </div>
          ) : (
            <div className="empty-state">
              <Search size={24} aria-hidden="true" />
              <h3>No matching sources found</h3>
              <p>Try another word or choose “All records.”</p>
              <button type="button" className="text-button" onClick={() => { setQuery(''); setActiveCategory('All records'); }}>Clear search and filters</button>
            </div>
          )}
        </section>

        <section className="about-section" id="about" aria-labelledby="about-title">
          <div className="about-copy">
            <p className="eyebrow">INDEPENDENT · COMMUNITY-MAINTAINED</p>
            <h2 id="about-title">A directory of sources, not a replacement for them.</h2>
            <p>
              Better Concepcion is an early civic technology prototype. The records remain with their original publishers; this page organizes selected links and shows when they were checked. It is not an official municipal service or partnership.
            </p>
            <a className="about-link" href="https://github.com/aaronher1030-glitch/bettergovtarlacph" target="_blank" rel="noreferrer">View project notes on GitHub <ArrowUpRight size={16} aria-hidden="true" /></a>
          </div>
          <div className="about-principles">
            <div><span>01</span><strong>Follow the original source</strong><p>Open the publisher’s page for the full record.</p></div>
            <div><span>02</span><strong>Make coverage visible</strong><p>Selected public pages only; not a complete archive.</p></div>
            <div><span>03</span><strong>Keep it informational</strong><p>No applications, payments, accounts, or personal-data forms.</p></div>
          </div>
        </section>

        <section className="caution-section" aria-label="Important information">
          <div className="caution-icon" aria-hidden="true"><ShieldCheck size={20} /></div>
          <div>
            <h2>Check the original source before relying on a record.</h2>
            <p>Links and summaries in this demo may be incomplete or become outdated. The demo does not provide official advice, handle transactions, or verify the completeness of the publisher’s records.</p>
          </div>
        </section>
      </main>

      <footer className="site-footer">
        <div className="footer-main">
          <div className="footer-project">
            <a className="footer-wordmark" href="#top">BETTER<span>CONCEPCION</span></a>
            <p>An independent prototype for finding public information about Concepcion, Tarlac.</p>
            <span className="footer-tag">EARLY DEMO · OPEN PROJECT</span>
          </div>
          <div className="footer-column"><h2>DIRECTORY</h2><a href="#categories">Browse topics</a><a href="#records">Public sources</a><a href="https://concepciontarlac.org/" target="_blank" rel="noreferrer">Official municipal site</a></div>
          <div className="footer-column"><h2>PROJECT</h2><a href="#about">About this demo</a><a href="https://github.com/aaronher1030-glitch/bettergovtarlacph" target="_blank" rel="noreferrer">GitHub repository</a><a href="#about">Limitations</a></div>
        </div>
        <div className="footer-bottom"><span>Independent community prototype · No LGU endorsement claimed</span><a href="https://concepciontarlac.org/" target="_blank" rel="noreferrer">Visit the official municipal website <ExternalLink size={14} aria-hidden="true" /></a></div>
      </footer>
    </>
  );
}

export default App;
