const API_BASE_URL = 'http://localhost:8000/api'

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL
  }

  getAuthHeaders(token) {
    const headers = {
      'Content-Type': 'application/json',
    }
    
    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }
    
    return headers
  }

  async request(endpoint, options = {}, token = null) {
    const url = `${this.baseURL}${endpoint}`
    
    const config = {
      ...options,
      headers: this.getAuthHeaders(token),
    }

    try {
      const response = await fetch(url, config)
      
      if (response.status === 401) {
        // Unauthorized - clear auth
        localStorage.removeItem('auth-storage')
        window.location.href = '/login'
        throw new Error('Unauthorized')
      }
      
      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || `HTTP ${response.status}`)
      }
      
      // Handle CSV downloads
      if (response.headers.get('content-type')?.includes('text/csv')) {
        return response.blob()
      }
      
      return await response.json()
    } catch (error) {
      console.error('API request failed:', error)
      throw error
    }
  }

  // Auth
  async login(username, password) {
    return this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    })
  }

  async register(data) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  async getCurrentUser(token) {
    return this.request('/auth/me', {}, token)
  }

  async getUsers(token) {
    return this.request('/auth/users', {}, token)
  }

  // Schemas
  async getSchemas(token) {
    return this.request('/schemas/', {}, token)
  }

  async getSchema(name, token) {
    return this.request(`/schemas/${name}`, {}, token)
  }

  async createSchema(data, token) {
    return this.request('/schemas/', {
      method: 'POST',
      body: JSON.stringify(data),
    }, token)
  }

  async updateSchema(name, data, token) {
    return this.request(`/schemas/${name}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }, token)
  }

  async deleteSchema(name, token) {
    return this.request(`/schemas/${name}`, {
      method: 'DELETE',
    }, token)
  }

  // Adaptors
  async getAdaptors(token) {
    return this.request('/adaptors/', {}, token)
  }

  async getAdaptor(containerId, token) {
    return this.request(`/adaptors/${containerId}`, {}, token)
  }

  async createAdaptor(data, token) {
    return this.request('/adaptors/', {
      method: 'POST',
      body: JSON.stringify(data),
    }, token)
  }

  async updateAdaptor(containerId, data, token) {
    return this.request(`/adaptors/${containerId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }, token)
  }

  async deleteAdaptor(containerId, token) {
    return this.request(`/adaptors/${containerId}`, {
      method: 'DELETE',
    }, token)
  }

  async getContainerCode(containerId, token) {
    return this.request(`/adaptors/${containerId}/code`, {}, token)
  }

  // Events
  async getEventStats(token, schemaId = null, days = 7) {
  const params = new URLSearchParams()
  if (schemaId) params.append('schema_id', schemaId)
  if (days) params.append('days', days)
  return this.request(`/events/stats?${params}`, {}, token)
  } 

  async getRecentEvents(token, schemaId = null, limit = 50) {
  const params = new URLSearchParams()
  if (schemaId) params.append('schema_id', schemaId)
  if (limit) params.append('limit', limit)
  return this.request(`/events/recent?${params}`, {}, token)
  }

  // Export
  async exportCSV(token, schemaId, eventType = null, days = 7) {
    const params = new URLSearchParams({ schema_id: schemaId, days })
    if (eventType) params.append('event_type', eventType)
    
    return this.request(`/export/csv?${params}`, {}, token)
  }

  async exportCSVFlattened(token, schemaId, eventType = null, days = 7) {
    const params = new URLSearchParams({ schema_id: schemaId, days })
    if (eventType) params.append('event_type', eventType)
    
    return this.request(`/export/csv/flattened?${params}`, {}, token)
  }
}

export default new ApiService()