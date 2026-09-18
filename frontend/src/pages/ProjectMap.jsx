import { useEffect, useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import mapboxgl from 'mapbox-gl'
import MapboxDraw from '@mapbox/mapbox-gl-draw'
import 'mapbox-gl/dist/mapbox-gl.css'
import '@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw.css'
import { getProject, createSite } from '../api/projects'

mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_TOKEN

export default function ProjectMap() {
  const { projectId } = useParams()
  const mapContainer = useRef(null)
  const mapRef = useRef(null)
  const drawRef = useRef(null)
  const [project, setProject] = useState(null)
  const [siteName, setSiteName] = useState('')
  const [pendingFeature, setPendingFeature] = useState(null)

  useEffect(() => {
    getProject(projectId).then(setProject)
  }, [projectId])

  useEffect(() => {
    if (mapRef.current || !mapContainer.current) return

    const map = new mapboxgl.Map({
      container: mapContainer.current,
      style: 'mapbox://styles/mapbox/satellite-streets-v12',
      center: [78.9629, 20.5937], // default: India
      zoom: 4,
    })
    mapRef.current = map

    const draw = new MapboxDraw({
      displayControlsDefault: false,
      controls: { polygon: true, trash: true },
    })
    drawRef.current = draw
    map.addControl(draw)

    map.on('draw.create', (e) => setPendingFeature(e.features[0]))
    map.on('draw.update', (e) => setPendingFeature(e.features[0]))
    map.on('draw.delete', () => setPendingFeature(null))

    return () => map.remove()
  }, [])

  // Render existing sites once loaded
  useEffect(() => {
    const map = mapRef.current
    if (!map || !project) return

    const renderExisting = () => {
      project.sites.forEach((site) => {
        const sourceId = `site-${site.id}`
        if (map.getSource(sourceId)) return
        map.addSource(sourceId, { type: 'geojson', data: site.geometry })
        map.addLayer({
          id: `${sourceId}-fill`,
          type: 'fill',
          source: sourceId,
          paint: { 'fill-color': '#1a7a4c', 'fill-opacity': 0.35 },
        })
        map.addLayer({
          id: `${sourceId}-line`,
          type: 'line',
          source: sourceId,
          paint: { 'line-color': '#1a7a4c', 'line-width': 2 },
        })
      })
    }

    if (map.isStyleLoaded()) renderExisting()
    else map.once('load', renderExisting)
  }, [project])

  const handleSaveSite = async (e) => {
    e.preventDefault()
    if (!pendingFeature) return
    await createSite(projectId, {
      name: siteName,
      geometry: pendingFeature.geometry,
    })
    setSiteName('')
    setPendingFeature(null)
    drawRef.current.deleteAll()
    getProject(projectId).then(setProject)
  }

  if (!project) return <p>Loading…</p>

  return (
    <div>
      <h2>{project.name}</h2>
      <p>{project.description}</p>

      <div className="map-container" ref={mapContainer} />

      {pendingFeature && (
        <form className="toolbar" onSubmit={handleSaveSite}>
          <input
            placeholder="Name this site"
            value={siteName}
            onChange={(e) => setSiteName(e.target.value)}
            required
          />
          <button type="submit">Save site</button>
        </form>
      )}

      <h3 style={{ marginTop: 24 }}>Sites</h3>
      <div className="site-list">
        {project.sites.length === 0 && <p>Draw a polygon on the map to add your first site.</p>}
        {project.sites.map((site) => (
          <Link
            key={site.id}
            to={`/projects/${projectId}/sites/${site.id}`}
            className="site-row"
          >
            <span>{site.name}</span>
            <span>{site.area_hectares ? `${site.area_hectares} ha` : '—'}</span>
          </Link>
        ))}
      </div>
    </div>
  )
}
