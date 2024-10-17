@minLength(1)
@description('Primary location for all resources')
param location string

@description('The AI Hub resource name.')
param hubName string
@description('The AI Project resource name.')
param projectName string
@description('The Key Vault resource name.')
param keyVaultName string
@description('The Storage Account resource name.')
param storageAccountName string
@description('The Open AI resource name.')
param openAiName string
@description('The Open AI connection name.')
param openAiConnectionName string
@description('The Open AI and serverless model deployments.')
param deployments array = []
@description('The Log Analytics resource name.')
param logAnalyticsName string = ''
@description('The Application Insights resource name.')
param applicationInsightsName string = ''
@description('The Container Registry resource name.')
param containerRegistryName string = ''
param tags object = {}
@description('The OpenAI API version')
param openaiApiVersion string = ''

var openaiDeployments = filter(deployments, deployment => toLower(deployment.platform) == 'openai')
var serverlessDeployments = filter(deployments, deployment => toLower(deployment.platform) == 'serverless')

module hubDependencies '../ai/hub-dependencies.bicep' = {
  name: 'hubDependencies'
  params: {
    location: location
    tags: tags
    keyVaultName: keyVaultName
    storageAccountName: storageAccountName
    containerRegistryName: containerRegistryName
    applicationInsightsName: applicationInsightsName
    logAnalyticsName: logAnalyticsName
    openAiName: openAiName
    openAiModelDeployments: openaiDeployments
  }
}

module hub '../ai/hub.bicep' = {
  name: 'hub'
  params: {
    location: location
    tags: tags
    name: hubName
    displayName: hubName
    keyVaultId: hubDependencies.outputs.keyVaultId
    storageAccountId: hubDependencies.outputs.storageAccountId
    containerRegistryId: hubDependencies.outputs.containerRegistryId
    applicationInsightsId: hubDependencies.outputs.applicationInsightsId
    openAiName: hubDependencies.outputs.openAiName
    openAiConnectionName: openAiConnectionName
  }
}

module project '../ai/project.bicep' = {
  name: 'project'
  params: {
    location: location
    tags: tags
    name: projectName
    displayName: projectName
    hubName: hub.outputs.name
    keyVaultName: hubDependencies.outputs.keyVaultName
  }
}

@batchSize(1)
module serverlessDeployment '../ai/serverless-deployment.bicep' = [for deployment in serverlessDeployments: {
  name: replace(deployment.name, '.', '-')
  params: {
    projectName: projectName
    modelId: deployment.model.?id
    modelName: deployment.model.?name
    registry: deployment.model.?registry
    endpointName: deployment.name
  }
  dependsOn: [
    project
  ]
}]

var serverlessDeploymentArray = [for (deployment, i) in serverlessDeployments: {
  name: deployment.name
  deployment: deployment
}]

// Index serverless deployments by their names
var serverlessDeploymentByName = mapValues(toObject(serverlessDeploymentArray, arg => arg.name), arg => arg.deployment)

// Outputs
// Resource Group
output resourceGroupName string = resourceGroup().name

// Hub
output hubName string = hub.outputs.name
output hubPrincipalId string = hub.outputs.principalId

// Project
output projectName string = project.outputs.name
output projectPrincipalId string = project.outputs.principalId

// Key Vault
output keyVaultName string = hubDependencies.outputs.keyVaultName
output keyVaultEndpoint string = hubDependencies.outputs.keyVaultEndpoint

// Application Insights
output applicationInsightsName string = hubDependencies.outputs.applicationInsightsName
output applicationInsightsConnectionString string = hubDependencies.outputs.applicationInsightsConnectionString
output logAnalyticsWorkspaceName string = hubDependencies.outputs.logAnalyticsWorkspaceName

// Container Registry
output containerRegistryName string = hubDependencies.outputs.containerRegistryName
output containerRegistryEndpoint string = hubDependencies.outputs.containerRegistryEndpoint

// Storage Account
output storageAccountName string = hubDependencies.outputs.storageAccountName

// Open AI
output openAiName string = hubDependencies.outputs.openAiName
output openAiEndpoint string = hubDependencies.outputs.openAiEndpoint

output serverlessDeployments array = [for (deployment, i) in serverlessDeployments: {
  name: deployment.name
  endpointUri: serverlessDeployment[i].outputs.endpointUri
  primaryKey: serverlessDeployment[i].outputs.primaryKey
  secondaryKey: serverlessDeployment[i].outputs.secondaryKey
}]

output openaiDeployments array = [for (deployment, i) in openaiDeployments: {
  name: deployment.name
  endpointUri: hubDependencies.outputs.openAiEndpoint
}]

output deployments array = [for (deployment, i) in deployments: union(deployment, {
  endpointUri: deployment.platform == 'serverless' ? serverlessDeploymentByName[deployment.name].outputs.endpointUri : hubDependencies.outputs.openAiEndpoint
  primaryKey: deployment.platform == 'serverless' ? serverlessDeploymentByName[deployment.name].outputs.primaryKey : ''
  secondaryKey: deployment.platform == 'serverless' ? serverlessDeploymentByName[deployment.name].outputs.secondaryKey : ''
  apiVersion: openaiApiVersion
})]
