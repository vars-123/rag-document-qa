import { type FormEvent, useMemo, useRef, useState } from 'react'

interface UploadZoneProps {
  onUpload: (file: File) => Promise<void>
}

export function UploadZone({ onUpload }: UploadZoneProps) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [uploading, setUploading] = useState(false)
  const [fileName, setFileName] = useState<string | null>(null)

  const helperText = useMemo(() => {
    if (uploading) {
      return 'Uploading the selected PDF...'
    }
    if (fileName) {
      return `Ready to upload ${fileName}`
    }
    return 'Choose a PDF to begin the document workflow.'
  }, [fileName, uploading])

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    const file = inputRef.current?.files?.[0]
    if (!file) return
    setUploading(true)
    try {
      await onUpload(file)
      setFileName(null)
      if (inputRef.current) inputRef.current.value = ''
    } finally {
      setUploading(false)
    }
  }

  return (
    <form className="upload-card" onSubmit={handleSubmit}>
      <div className="upload-copy">
        <h2>Upload a PDF</h2>
        <p>PDF only. Large files are capped at 10 MB for now.</p>
      </div>

      <label className="upload-dropzone" htmlFor="pdf-upload">
        <input
          id="pdf-upload"
          ref={inputRef}
          type="file"
          accept="application/pdf"
          disabled={uploading}
          onChange={() => {
            const file = inputRef.current?.files?.[0]
            setFileName(file?.name ?? null)
          }}
        />
      </label>

      <div className="upload-meta">
        <span>{helperText}</span>
        <button className="primary-button" type="submit" disabled={uploading || !fileName}>
          {uploading ? 'Uploading…' : 'Upload PDF'}
        </button>
      </div>
    </form>
  )
}
