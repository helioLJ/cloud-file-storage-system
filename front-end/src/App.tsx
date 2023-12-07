import { useEffect, useState } from 'react'
import { FileList } from './components/FileList'
import { UploadForm } from './components/UploadForm'

export function App() {
  const [files, setFiles] = useState<null | MyFile[]>(null)

  async function listFiles() {
    return fetch('http://localhost:5000/list_files')
      .then((response) => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`)
        }
        return response.json()
      })
      .then((data) => {
        console.log('Lista de arquivos:', data)
        setFiles(data)
        return data
      })
      .catch((error) => {
        console.error('Erro ao obter a lista de arquivos:', error)
      })
  }

  async function handleUploadComplete() {
    // Atualize a lista de arquivos após o upload
    await listFiles()
  }

  useEffect(() => {
    // Exemplo de uso
    listFiles()
  }, [])

  return (
    <div className="bg-zinc-800 w-full h-screen text-white flex justify-center items-center">
      <div className="w-[500px] flex flex-col gap-4">
        <h1 className="text-center text-4xl font-bold">
          Cloud File Storage System
        </h1>
        <h2 className="text-center mb-6">
          Python + Flask + S3 + DynamoDB + Lambda Function
        </h2>
        <UploadForm onUploadComplete={handleUploadComplete} />
        <FileList onUploadComplete={handleUploadComplete} files={files} />
      </div>
    </div>
  )
}
