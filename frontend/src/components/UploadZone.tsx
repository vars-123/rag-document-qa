import { type FormEvent, useRef, useState } from 'react'

interface UploadZoneProps {
  onUpload: (file: File) => Promise<void>
}

export function UploadZone({ onUpload }: UploadZoneProps) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [uploading, setUploading] = useState(false)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    const file = inputRef.current?.files?.[0]
    if (!file) return
    setUploading(true)
    try {
      await onUpload(file)
      if (inputRef.current) inputRef.current.value = ''
    } finally {
      setUploading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        ref={inputRef}
        type="file"
        accept="application/pdf"
        disabled={uploading}
      />
      <button type="submit" disabled={uploading}>
        {uploading ? 'Uploading...' : 'Upload'}
      </button>
    </form>
  )
}
