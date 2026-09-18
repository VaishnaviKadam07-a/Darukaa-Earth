import client from './client'

export const listProjects = () => client.get('/api/projects').then((r) => r.data)
export const getProject = (id) => client.get(`/api/projects/${id}`).then((r) => r.data)
export const createProject = (payload) =>
  client.post('/api/projects', payload).then((r) => r.data)
export const deleteProject = (id) => client.delete(`/api/projects/${id}`)

export const createSite = (projectId, payload) =>
  client.post(`/api/projects/${projectId}/sites`, payload).then((r) => r.data)
export const listSites = (projectId) =>
  client.get(`/api/projects/${projectId}/sites`).then((r) => r.data)
export const getSiteMetrics = (projectId, siteId) =>
  client.get(`/api/projects/${projectId}/sites/${siteId}/metrics`).then((r) => r.data)
