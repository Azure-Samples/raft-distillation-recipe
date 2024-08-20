@description('The Azure AI Studio project name')
param projectName string = 'my-project'
@description('The Azure AI Model catalog asset id')
param modelId string = 'azureml://registries/azureml-meta/models/Meta-Llama-3-8B-Instruct'

var modelName = substring(modelId, (lastIndexOf(modelId, '/') + 1))
var subscriptionName = '${modelName}-subscription'

resource marketplace_subscription 'Microsoft.MachineLearningServices/workspaces/marketplaceSubscriptions@2024-04-01-preview' = if (!startsWith(
  modelId,
  'azureml://registries/azureml/'
)) {
  name: '${projectName}/${subscriptionName}'
  properties: {
    modelId: modelId
  }
}
