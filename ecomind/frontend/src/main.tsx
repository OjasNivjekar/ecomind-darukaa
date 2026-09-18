import { FormEvent, useMemo, useState } from 'react'
import { createRoot } from 'react-dom/client'
import './styles.css'

type Recommendation = { action:string; why_it_works:string; impacted_metrics:string[]; time_horizon:string; confidence:string; citations:string[] }
type Result = { reply:string; needs_clarification:boolean; assessment:string; key_interactions:string[]; recommendations:Recommendation[]; impacted_metrics:string[]; confidence:string; sources:{id:string;label:string;title:string;organization:string;year:string;url:string;excerpt:string}[]; llm_used:boolean }
type FollowUp = { user:string; assistant:string; result:Result }
type Conversation = { id:string; sessionId:string; originalInput:string; result:Result; followUps:FollowUp[] }
const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

function titleFor(input:string) {
  const text = input.toLowerCase()
  if (text.includes('mango') || text.includes('orchard')) return 'Mango orchard biodiversity assessment'
  if (text.includes('river') || text.includes('riparian')) return 'River ecosystem assessment'
  return input.length > 64 ? `${input.slice(0, 61)}...` : input
}

function assistantSummary(result:Result) {
  const focus = result.recommendations.slice(0, 2).map(item => item.action).join(' ')
  return focus ? `${result.reply} Recommended focus: ${focus}` : result.reply
}

function App() {
  const [query, setQuery] = useState('')
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [activeId, setActiveId] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [followUp, setFollowUp] = useState('')
  const [jsonOpen, setJsonOpen] = useState(false)
  const [json, setJson] = useState('')
  const [error, setError] = useState('')
  const active = useMemo(() => conversations.find(item => item.id === activeId) ?? null, [conversations, activeId])

  async function requestAssessment(input:string, sessionId:string, environmental_data:Record<string, unknown> = {}) {
    const response = await fetch(`${API}/api/analyze`, { method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({query:input, environmental_data, session_id:sessionId}) })
    if (!response.ok) throw new Error('The assessment service could not process this request.')
    return response.json() as Promise<Result>
  }

  async function submitInitial(event:FormEvent) {
    event.preventDefault(); if (!query.trim()) return
    setLoading(true); setError('')
    try {
      const environmentalData = json.trim() ? JSON.parse(json) : {}
      const input = query.trim(); const id = crypto.randomUUID(); const sessionId = crypto.randomUUID()
      const result = await requestAssessment(input, sessionId, environmentalData)
      setConversations(current => [...current, {id, sessionId, originalInput:input, result, followUps:[]}])
      setActiveId(id); setQuery(''); setJson(''); setJsonOpen(false)
    } catch (err) { setError(err instanceof Error ? err.message : 'Unable to submit query.') }
    finally { setLoading(false) }
  }

  async function submitFollowUp(event:FormEvent) {
    event.preventDefault(); if (!active || !followUp.trim()) return
    setLoading(true); setError('')
    try {
      const input = followUp.trim(); const latestResult = active.followUps.length ? active.followUps[active.followUps.length - 1].result : active.result; const result = await requestAssessment(input, active.sessionId, latestResult.environmental_data as Record<string, unknown>)
      const turn:FollowUp = {user:input, assistant:assistantSummary(result), result}
      setConversations(current => current.map(item => item.id === active.id ? {...item, followUps:[...item.followUps, turn]} : item))
      setFollowUp('')
    } catch (err) { setError(err instanceof Error ? err.message : 'Unable to send follow-up.') }
    finally { setLoading(false) }
  }

  const source = (id:string, result:Result = active?.result as Result) => result?.sources.find(item => item.id === id)
  return <main className={active ? 'layout panel-open' : 'layout'}>
    <section className="landing">
      <div className="brand"><div className="mark">O</div><h1>EcoMind</h1><p className="eyebrow">Biodiversity Intelligence Advisor</p></div>
      <p className="intro">Analyze environmental conditions and receive evidence-backed biodiversity interventions grounded in scientific knowledge.</p>
      <form onSubmit={submitInitial} className="query-form"><textarea value={query} onChange={e=>setQuery(e.target.value)} onKeyDown={e=>{if(e.key==='Enter' && !e.shiftKey) submitInitial(e)}} placeholder="Describe your land, soil, climate or biodiversity situation..." aria-label="Environmental query"/><button disabled={loading}>{loading ? 'Analyzing...' : 'Analyze'}</button></form>
      <button className="structured" onClick={()=>setJsonOpen(!jsonOpen)}>Structured environmental input {jsonOpen ? '-' : '+'}</button>
      {jsonOpen && <textarea className="json" value={json} onChange={e=>setJson(e.target.value)} placeholder={'{"soil_organic_carbon": 0.3, "rainfall": "low", "land_use": "monoculture"}'} />}
      {error && <p className="error">{error}</p>}
      <p className="hint">Enter to analyze · Shift + Enter for a new line</p>
      {conversations.length > 0 && <nav className="history" aria-label="Conversation history"><p>Assessment history</p>{conversations.map(item => <button key={item.id} className={item.id === activeId ? 'history-item active' : 'history-item'} onClick={()=>setActiveId(item.id)}><span>{titleFor(item.originalInput)}</span><small>{item.followUps.length ? `${item.followUps.length} follow-up${item.followUps.length === 1 ? '' : 's'}` : 'Original assessment'}</small></button>)}</nav>}
    </section>
    {active && <aside className="result-panel" aria-label="Biodiversity assessment workspace">
      <div className="panel-content"><button className="close" onClick={()=>setActiveId(null)} aria-label="Close assessment">x</button>
        <header><span>ECOMIND / ANALYSIS</span><p>{active.result.llm_used ? 'Llama synthesis with grounded evidence' : 'Structured reasoning with local evidence'}</p></header>
        <section className="original-input"><h2>Original input</h2><p>{active.originalInput}</p></section>
        {active.result.needs_clarification && <div className="clarification"><strong>Clarification needed</strong><p>{active.result.reply}</p></div>}
        <section><h2>Assessment</h2><p className="assessment">{active.result.assessment}</p></section>
        <section><h2>Key environmental interactions</h2>{active.result.key_interactions.length ? active.result.key_interactions.map((item,i)=><p className="interaction" key={i}>{item}</p>) : <p>More environmental inputs are needed to identify a specific interaction.</p>}</section>
        {!active.result.needs_clarification && <section><h2>Recommendations</h2>{active.result.recommendations.map((rec,i)=><article className="recommendation" key={i}><h3>{rec.action}</h3><p>{rec.why_it_works}</p><dl><dt>Impacted metrics</dt><dd>{rec.impacted_metrics.join(' · ')}</dd><dt>Time horizon</dt><dd>{rec.time_horizon}</dd><dt>Confidence</dt><dd>{rec.confidence}</dd></dl><p className="citations">{rec.citations.map((id,j)=>{const item=source(id); return item ? <a key={id} href={item.url} target="_blank" rel="noreferrer">[{j+1}] {item.organization}</a> : null})}</p></article>)}</section>}
        <section><h2>Sources / evidence</h2>{active.result.sources.map(item=><a className="source" key={item.id} href={item.url} target="_blank" rel="noreferrer"><span>{item.label}</span><div><strong>{item.title}</strong><p>{item.organization} · {item.year}</p><small>{item.excerpt}</small></div></a>)}</section>
        {active.followUps.length > 0 && <section className="conversation"><h2>Conversation</h2>{active.followUps.map((turn,index)=><div className="turn" key={index}><div className="turn-user"><span>You</span><p>{turn.user}</p></div><div className="turn-assistant"><span>EcoMind</span><p>{turn.assistant}</p></div></div>)}</section>}
      </div>
      <form className="followup-form" onSubmit={submitFollowUp}><textarea value={followUp} onChange={e=>setFollowUp(e.target.value)} onKeyDown={e=>{if(e.key==='Enter' && !e.shiftKey) submitFollowUp(e)}} placeholder="Ask a follow-up about this assessment..." aria-label="Follow-up question"/><button disabled={loading || !followUp.trim()} aria-label="Send follow-up">Send</button></form>
    </aside>}
  </main>
}
createRoot(document.getElementById('root')!).render(<App />)
