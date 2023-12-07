import { ChangeEvent, useState } from 'react'

export function UploadForm({
  onUploadComplete,
}: {
  onUploadComplete: () => Promise<void>
}) {
  const [file, setFile] = useState<null | File>(null)

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0] // Use optional chaining
    if (selectedFile) {
      setFile(selectedFile)
    }
  }

  const handleUpload = () => {
    if (file) {
      const formData = new FormData()
      formData.append('file', file)

      fetch('http://localhost:5000/upload', {
        method: 'POST',
        body: formData,
      })
        .then((response) => response.json())
        .then((data) => {
          console.log('Upload bem-sucedido:', data)
          onUploadComplete()
        })
        .catch((error) => {
          console.error('Erro no upload:', error)
        })
    }
  }

  return (
    <div className="w-full mx-auto p-6 bg-white border rounded shadow-md">
      <h2 className="text-2xl text-zinc-700 font-semibold mb-4">
        Upload de Arquivos
      </h2>

      <label
        htmlFor="fileInput"
        className="block text-sm font-medium text-gray-700 mb-2"
      >
        Escolher arquivo
      </label>
      <input
        type="file"
        id="fileInput"
        className="border text-zinc-700 rounded p-2 w-full"
        onChange={handleFileChange}
      />

      <button
        onClick={handleUpload}
        className="mt-4 bg-blue-500 text-white rounded px-4 py-2 hover:bg-blue-600 focus:outline-none focus:shadow-outline-blue active:bg-blue-800"
      >
        Enviar
      </button>
    </div>
  )
}
