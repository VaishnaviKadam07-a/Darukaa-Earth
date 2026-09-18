import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { listProjects, createProject } from '../api/projects'

export default function Dashboard() {
  const [projects, setProjects] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [projectType, setProjectType] = useState('carbon')
  const [loading, setLoading] = useState(true)

  const refresh = () => listProjects().then(setProjects).finally(() => setLoading(false))

  useEffect(() => {
    refresh()
  }, [])

  const handleCreate = async (e) => {
    e.preventDefault()
    await createProject({ name, description, project_type: projectType })
    setName('')
    setDescription('')
    setShowForm(false)
    refresh()
  }

  return (
    <div>
      <div className="toolbar">
        <h2 style={{ flex: 1 }}>Your projects</h2>
        <button onClick={() => setShowForm((s) => !s)}>
          {showForm ? 'Cancel' : '+ New project'}
        </button>
      </div>

      {showForm && (
        <form className="auth-form" onSubmit={handleCreate}>
          <input
            placeholder="Project name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
          <input
            placeholder="Description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
          <select value={projectType} onChange={(e) => setProjectType(e.target.value)}>
            <option value="carbon">Carbon</option>
            <option value="biodiversity">Biodiversity</option>
          </select>
          <button type="submit">Create</button>
        </form>
      )}

      {loading ? (
        <p>Loading…</p>
      ) : projects.length === 0 ? (
        <p>No projects yet — create one to add sites on the map.</p>
      ) : (
        <div className="project-grid">
          {projects.map((p) => (
            <Link key={p.id} to={`/projects/${p.id}`} className="project-card">
              <h3>{p.name}</h3>
              <p>{p.description || 'No description'}</p>
              <span className="badge">
                {p.project_type} · {p.site_count} site{p.site_count === 1 ? '' : 's'}
              </span>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
