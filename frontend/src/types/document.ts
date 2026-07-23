export interface DocumentResponse {
  id: string
  filename: string
  status: string
  uploaded_at: string
  chunk_count: number
  error: string | null
}
