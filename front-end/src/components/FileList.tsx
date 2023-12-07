interface FileListProps {
  files: MyFile[] | null
  onUploadComplete: () => Promise<void>
}

export function FileList({ files, onUploadComplete }: FileListProps) {
  function onDownload(file: MyFile) {
    // Realiza o download do arquivo
    fetch(`http://localhost:5000/download/${file.filename}`)
      .then((response) => response.blob())
      .then((blob) => {
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', file.filename)
        document.body.appendChild(link)
        link.click()
      })
      .catch((error) => {
        console.error('Erro ao fazer o download do arquivo', error)
      })
  }

  function onDelete(file: MyFile) {
    // Exclui o arquivo
    fetch(`http://localhost:5000//delete_file/${file.filename}`, {
      method: 'DELETE',
    })
      .then((response) => {
        if (response.ok) {
          console.log('Arquivo excluído com sucesso')
          onUploadComplete()
        } else {
          throw new Error('Erro ao excluir o arquivo')
        }
      })
      .catch((error) => {
        console.error(error.message)
      })
  }

  return (
    <div className="w-full mx-auto p-6 bg-white border rounded shadow-md">
      <h2 className="text-2xl font-semibold mb-4 text-zinc-700">
        Lista de Arquivos
      </h2>
      <ul>
        {files &&
          files.map((file: MyFile) => (
            <li
              key={file.filename}
              className="flex items-center flex-col gap-2 justify-between bg-gray-100 border-b p-2"
            >
              <span className="text-gray-800 self-start">{file.filename}</span>
              <div className="space-x-2">
                <button
                  onClick={() => onDownload(file)}
                  className="bg-blue-500 text-white rounded px-3 py-1 hover:bg-blue-600 focus:outline-none focus:shadow-outline-blue active:bg-blue-800"
                >
                  Download
                </button>
                <button
                  onClick={() => onDelete(file)}
                  className="bg-red-500 text-white rounded px-3 py-1 hover:bg-red-600 focus:outline-none focus:shadow-outline-red active:bg-red-800"
                >
                  Excluir
                </button>
              </div>
            </li>
          ))}
      </ul>
    </div>
  )
}
