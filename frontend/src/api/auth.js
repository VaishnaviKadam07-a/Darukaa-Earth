import client from './client'

export async function register(email, password, fullName) {
  const { data } = await client.post('/api/auth/register', {
    email,
    password,
    full_name: fullName,
  })
  return data
}

export async function login(email, password) {
  const form = new URLSearchParams()
  form.append('username', email)
  form.append('password', password)
  const { data } = await client.post('/api/auth/login', form, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  localStorage.setItem('access_token', data.access_token)
  return data
}

export function logout() {
  localStorage.removeItem('access_token')
}

export function isAuthenticated() {
  return Boolean(localStorage.getItem('access_token'))
}
