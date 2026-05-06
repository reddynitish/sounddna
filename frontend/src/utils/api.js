const BASE_URL = import.meta.env.VITE_API_URL || '/api'

export async function analyzeSong(url, timestamp = null) {
  const response = await fetch(`${BASE_URL}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url, timestamp }),
  })

  if (!response.ok) {
    const err = await response.json().catch(() => ({}))
    throw new Error(err.detail || `Server error ${response.status}`)
  }

  return response.json()
}
