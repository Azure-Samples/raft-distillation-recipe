@description('The Azure AI Studio project name')
param projectName string = 'my-project'

@description('The Azure AI Model catalog asset id')
param modelId string = 'azureml://registries/azureml-meta/models/Meta-Llama-3-8B-Instruct'

@description('The serverless endpoint name')
param endpointName string = ''

@description('The serverless deployment location')
param location string = resourceGroup().location

var modelName = substring(modelId, (lastIndexOf(modelId, '/') + 1))
var subscriptionName = '${modelName}-subscription'
var endpointName_ = !empty(endpointName) ? endpointName : take(replace(replace(modelName, '_', '-'), '.', '-'), 64)

resource marketplace_subscription 'Microsoft.MachineLearningServices/workspaces/marketplaceSubscriptions@2024-04-01-preview' = if (!startsWith(
  modelId,
  'azureml://registries/azureml/'
)) {
  name: '${projectName}/${subscriptionName}'
  properties: {
    modelId: modelId
  }
}

resource maas_endpoint 'Microsoft.MachineLearningServices/workspaces/serverlessEndpoints@2024-04-01-preview' = {
  name: '${projectName}/${endpointName_}'
  location: location
  sku: {
    name: 'Consumption'
  }
  properties: {
    modelSettings: {
      modelId: modelId
    }
  }
  dependsOn: [
    marketplace_subscription
  ]
}

output endpointUri string = maas_endpoint.properties.inferenceEndpoint.uri
