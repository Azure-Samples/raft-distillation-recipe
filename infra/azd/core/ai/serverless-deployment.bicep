@description('The Azure AI Studio project name')
param projectName string = 'my-project'

@description('The Azure AI Model catalog asset id')
param modelId string = ''

@description('The Azure AI Model name')
param modelName string = ''

@description('The Azure AI Model registry')
param registry string = ''

@description('The serverless endpoint name')
@maxLength(32)
param endpointName string = ''

@description('The serverless deployment location')
param location string = resourceGroup().location

var modelId_ = !empty(modelId) ? modelId : 'azureml://registries/${registry}/models/${modelName}'
var subscriptionName = '${modelName}-subscription'
var endpointName_ = !empty(endpointName) ? endpointName : take(replace(replace('${modelName}', '_', '-'), '.', '-'), 32)

resource marketplace_subscription 'Microsoft.MachineLearningServices/workspaces/marketplaceSubscriptions@2024-04-01-preview' = if (!startsWith(
  modelId_,
  'azureml://registries/azureml/'
)) {
  name: replace('${projectName}/${subscriptionName}', '.', '-')
  properties: {
    modelId: modelId_
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
      modelId: modelId_
    }
  }
  dependsOn: [
    marketplace_subscription
  ]
}

output endpointUri string = maas_endpoint.properties.inferenceEndpoint.uri
output primaryKey string = maas_endpoint.listKeys().primaryKey
output secondaryKey string = maas_endpoint.listKeys().secondaryKey
