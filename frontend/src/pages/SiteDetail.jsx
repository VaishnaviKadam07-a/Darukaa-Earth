import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
  Title,
} from 'chart.js'
import { getSiteMetrics, getProject } from '../api/projects'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend, Title)

export default function SiteDetail() {
  const { projectId, siteId } = useParams()
  const [metrics, setMetrics] = useState([])
  const [siteName, setSiteName] = useState('')

  useEffect(() => {
    getSiteMetrics(projectId, siteId).then(setMetrics)
    getProject(projectId).then((p) => {
      const site = p.sites.find((s) => s.id === siteId)
      if (site) setSiteName(site.name)
    })
  }, [projectId, siteId])

  const labels = metrics.map((m) => new Date(m.recorded_at).toLocaleDateString())

  const carbonData = {
    labels,
    datasets: [
      {
        label: 'Carbon sequestered (tons)',
        data: metrics.map((m) => m.carbon_tons),
        borderColor: '#1a7a4c',
        backgroundColor: 'rgba(26,122,76,0.15)',
        tension: 0.3,
      },
    ],
  }

  const biodiversityData = {
    labels,
    datasets: [
      {
        label: 'Biodiversity index',
        data: metrics.map((m) => m.biodiversity_index),
        borderColor: '#2b6cb0',
        backgroundColor: 'rgba(43,108,176,0.15)',
        tension: 0.3,
      },
      {
        label: 'NDVI (vegetation health)',
        data: metrics.map((m) => m.ndvi),
        borderColor: '#b7791f',
        backgroundColor: 'rgba(183,121,31,0.15)',
        tension: 0.3,
      },
    ],
  }

  return (
    <div>
      <Link to={`/projects/${projectId}`}>&larr; Back to project</Link>
      <h2>{siteName || 'Site'}</h2>

      {metrics.length === 0 ? (
        <p>No analytics data yet for this site.</p>
      ) : (
        <>
          <div className="chart-block">
            <Line data={carbonData} />
          </div>
          <div className="chart-block">
            <Line data={biodiversityData} />
          </div>
        </>
      )}
    </div>
  )
}
