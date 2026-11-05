import { useEffect, useRef, useState } from 'react'
import { Menu, X, Copy, Check } from 'lucide-react'
import { ArrowRight, UploadCloud, FileText, CheckCircle2, XCircle, Sparkles, Target, BrainCircuit, ShieldCheck, LoaderCircle, RotateCcw } from 'lucide-react'

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

function App() {
  const inputRef = useRef(null)
  const [file, setFile] = useState(null)
  const [jobDescription, setJobDescription] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const resultRef = useRef(null)
  const [menuOpen, setMenuOpen] = useState(false)
  const [dragging, setDragging] = useState(false)
  const [copied, setCopied] = useState(false)
  const score = Number(result?.match_score ?? 0)
  const scoreLevel = score >= 70 ? 'high' : score >= 40 ? 'medium' : 'low'

  useEffect(() => {
    if (result) resultRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }, [result])

  function chooseFile(selected) {
    setError('')
    setResult(null)
    if (!selected) return
    if (selected.type !== 'application/pdf' && !selected.name.toLowerCase().endsWith('.pdf')) {
      setError('Please upload a PDF file only.')
      return
    }
    if (selected.size > 10 * 1024 * 1024) {
      setError('File size must be 10 MB or less.')
      return
    }
    setFile(selected)
  }

  async function handleAnalyze(event) {
    event.preventDefault()
    setError('')
    setResult(null)
    if (!file) return setError('Please upload your CV first.')
    if (!jobDescription.trim()) return setError('Please paste the job description first.')

    const data = new FormData()
    data.append('cv', file)
    data.append('job_description', jobDescription)
    setLoading(true)
    try {
      const response = await fetch(`${API_URL}/analyze`, { method: 'POST', body: data })
      const payload = await response.json()
      if (!response.ok) throw new Error(payload.detail || 'Something went wrong during the analysis.')
      setResult(payload)
    } catch (err) {
      setError(err.message.includes('Failed to fetch')
        ? 'Cannot reach the server. Please make sure the backend is running.'
        : err.message)
    } finally {
      setLoading(false)
    }
  }

  async function copyResults() {
    const list = items => (items && items.length ? items.join(', ') : '-')
    const text = [
      `Match score: ${result.match_score}%`,
      `Matching skills: ${list(result.matched_skills)}`,
      `Missing skills: ${list(result.missing_skills)}`,
      'Suggestions:',
      ...(result.suggestions || []).map(s => `- ${s}`),
    ].join('\n')
    try {
      await navigator.clipboard.writeText(text)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      setError('Could not copy the results. Please copy them manually.')
    }
  }

  function reset() {
    setFile(null); setJobDescription(''); setResult(null); setError('')
    if (inputRef.current) inputRef.current.value = ''
  }

  return (
    <div className="app-shell">
      <header className="site-header">
      <nav className="navbar">
        <a className="brand" href="#"><span className="brand-mark"><BrainCircuit size={21}/></span> Career<span>Match</span></a>
        <button type="button" className="menu-toggle" aria-label="Toggle menu" aria-expanded={menuOpen} onClick={() => setMenuOpen(o => !o)}>{menuOpen ? <X size={22}/> : <Menu size={22}/>}</button>
        <div className={`nav-right ${menuOpen ? 'open' : ''}`} onClick={() => setMenuOpen(false)}><a href="#">Home</a><a href="#how-it-works">How it works</a><a href="#about">About</a><a className="nav-cta" href="#analyzer">Try it <ArrowRight size={15}/></a></div>
      </nav>
      </header>

      <main>
        <section className="hero">
          <div className="hero-copy">
            <div className="eyebrow"><Sparkles size={15}/> SMART CAREER TOOL</div>
            <h1>Make your next career move <span>with confidence.</span></h1>
            <p>Discover how well your CV matches a job description. Find your strengths, spot missing skills, and get practical suggestions to improve.</p>
            <a className="primary-link" href="#analyzer">Analyze my CV <ArrowRight size={17}/></a>
            <div className="trust-line"><ShieldCheck size={16}/> Your CV is analyzed for this session only.</div>
          </div>
          <div className="hero-visual">
            <div className="visual-glow"></div>
            <div className="floating-card top-card"><span className="mini-icon"><Target size={18}/></span><div><b>Career clarity</b><small>Know where you stand</small></div></div>
            <div className="score-card"><div className="score-top"><span>SAMPLE PREVIEW</span><Sparkles size={17}/></div><div className="score-ring"><div><strong>85%</strong><small>Match score</small></div></div><div className="score-bars"><i/><i/><i/></div><div className="score-caption">A clearer path to your next role</div></div>
            <div className="floating-card bottom-card"><span className="check-icon"><CheckCircle2 size={18}/></span><div><b>Skill insights</b><small>Strengths & opportunities</small></div></div>
          </div>
        </section>

        <section className="steps-section" id="how-it-works">
          <div className="section-heading"><span className="eyebrow">SIMPLE BY DESIGN</span><h2>How it works</h2><p>Three simple steps to understand your job fit.</p></div>
          <div className="steps-grid">
            <article className="step-card"><span className="step-number">01</span><div className="step-icon"><UploadCloud/></div><h3>Upload your CV</h3><p>Upload your CV as a PDF file so we can read your experience and skills.</p></article>
            <article className="step-card"><span className="step-number">02</span><div className="step-icon"><FileText/></div><h3>Add the job description</h3><p>Paste the job requirements for the role you want to apply for.</p></article>
            <article className="step-card"><span className="step-number">03</span><div className="step-icon"><Target/></div><h3>Get your insights</h3><p>See your matching skills, missing skills, and improvement suggestions.</p></article>
          </div>
        </section>

        <section className="analyzer-section" id="analyzer">
          <div className="section-heading"><span className="eyebrow">LET'S GET STARTED</span><h2>Analyze your career match</h2><p>Give us the two things we need to get your results.</p></div>
          <form className="analyzer-card" onSubmit={handleAnalyze}>
            <div className="form-grid">
              <div className="field-block">
                <label>01 <span>YOUR CV</span></label>
                <button type="button" className={`upload-box ${file ? 'has-file' : ''} ${dragging ? 'dragging' : ''}`} onClick={() => inputRef.current?.click()} onDragOver={e => {e.preventDefault(); setDragging(true)}} onDragLeave={() => setDragging(false)} onDrop={e => {e.preventDefault(); setDragging(false); chooseFile(e.dataTransfer.files?.[0])}}>
                  {file ? <><CheckCircle2 className="upload-symbol success"/><strong>{file.name}</strong><small>{(file.size / 1024 / 1024).toFixed(2)} MB · Click to change</small></> : <><UploadCloud className="upload-symbol"/><strong>Click to upload or drag your CV here</strong><small>PDF only · Maximum file size 10 MB</small></>}
                </button>
                <input ref={inputRef} type="file" accept=".pdf,application/pdf" hidden onChange={e => chooseFile(e.target.files?.[0])}/>
              </div>
              <div className="field-block">
                <label>02 <span>JOB DESCRIPTION</span></label>
                <textarea value={jobDescription} onChange={e => setJobDescription(e.target.value)} placeholder="Paste the job description here...&#10;&#10;Example: We are looking for a Python developer with experience in FastAPI, SQL, and machine learning."/>
                <small className="field-hint">Include the responsibilities and required skills for better insights.</small>
              </div>
            </div>
            {error && <div className="error-message"><XCircle size={17}/>{error}</div>}
            <button className="analyze-button" type="submit" disabled={loading}>{loading ? <><LoaderCircle className="spin" size={18}/> Analyzing...</> : <>Analyze my match <ArrowRight size={18}/></>}</button>
          </form>

          {result && <section className="results-card" ref={resultRef} aria-live="polite">
            <div className="results-heading"><div><span className="eyebrow">YOUR RESULTS</span><h2>Here is your match breakdown</h2></div><div className="results-actions"><button type="button" className="reset-button" onClick={copyResults}>{copied ? <><Check size={15}/> Copied</> : <><Copy size={15}/> Copy results</>}</button><button type="button" className="reset-button" onClick={reset}><RotateCcw size={15}/> New analysis</button></div></div>
            <div className="result-score">
              <div className={`score-ring-lg ${scoreLevel}`} style={{ '--p': score }}><span>{result.match_score}%</span></div>
              <div className="result-score-info">
                <b>Overall skill match</b>
                <span className={`level-badge ${scoreLevel}`}>{scoreLevel === 'high' ? 'Strong match' : scoreLevel === 'medium' ? 'Partial match' : 'Low match'}</span>
                <p>{result.note}</p>
              </div>
            </div>
            <div className="result-columns">
              <div><h3><CheckCircle2/> Matching skills ({result.matched_skills.length})</h3><div className="chips">{result.matched_skills.length ? result.matched_skills.map(s=><span className="chip good" key={s}>{s}</span>) : <p className="empty-state">No matching skills detected yet.</p>}</div></div>
              <div><h3><XCircle/> Skills to develop ({result.missing_skills.length})</h3><div className="chips">{result.missing_skills.length ? result.missing_skills.map(s=><span className="chip missing" key={s}>{s}</span>) : <p className="empty-state">No missing skills detected from the supported list.</p>}</div></div>
            </div>
            <div className="suggestions"><h3><Sparkles/> Suggestions to improve</h3><ul>{result.suggestions.map((s,i)=><li key={i}>{s}</li>)}</ul></div>
          </section>}
        </section>


        <section className="about-section" id="about">
          <div className="section-heading"><span className="eyebrow">ABOUT THE PROJECT</span><h2>About AI Career Match</h2><p>An educational project that helps job seekers understand how well their CV fits a role.</p></div>
          <div className="about-grid">
            <article className="about-card"><h3>Our goal</h3><p>Make it easier to see which skills you already have for a job and which ones are worth developing next.</p></article>
            <article className="about-card"><h3>How it works</h3><p>The system reads your CV and compares the skills it finds with the skills mentioned in the job description.</p></article>
            <article className="about-card"><h3>Your privacy</h3><p>Your CV is used only to produce your result in this session. It is not shown to anyone else.</p></article>
          </div>
        </section>
      </main>
      <footer><a className="brand" href="#"><span className="brand-mark"><BrainCircuit size={18}/></span> Career<span>Match</span></a><p>Built as an educational AI & Cloud Computing project.</p><small>© 2026 AI Career Match</small></footer>
    </div>
  )
}

export default App
