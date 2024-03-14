import * as fs from 'node:fs'

const filePath = './openapi.json'

fs.readFile(filePath, (err, data) => {
  const openapiContent = JSON.parse(data)
  if (err) throw err

  const paths = openapiContent.paths

  for (const pathKey of Object.keys(paths)) {
    const pathData = paths[pathKey]
    for (const method of Object.keys(pathData)) {
      const operation = pathData[method]
      if (operation.tags && operation.tags.length > 0) {
        const tag = operation.tags[0]
        const operationId = operation.operationId
        const toRemove = `${tag}-`
        if (operationId.startsWith(toRemove)) {
          const newOperationId = operationId.substring(toRemove.length)
          operation.operationId = newOperationId
        }
      }
    }
  }
  fs.writeFile(filePath, JSON.stringify(openapiContent, null, 2), (err) => {
    if (err) throw err
  })
})
