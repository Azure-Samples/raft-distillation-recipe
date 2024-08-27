targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name which is used to generate a short unique hash for each resource')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
@metadata({
  azd: {
    type: 'location'
  }
})
param location string

param containerRegistryName string = ''
param aiHubName string = ''
@description('The Azure AI Studio project name. If ommited will be generated')
param aiProjectName string = ''
@description('The application insights resource name. If ommited will be generated')
param applicationInsightsName string = ''
@description('The Open AI resource name. If ommited will be generated')
param openAiName string = ''
@description('The Open AI connection name. If ommited will use a default value')
param openAiConnectionName string = ''
param keyVaultName string = ''
@description('The Azure Storage Account resource name. If ommited will be generated')
param storageAccountName string = ''

var abbrs = loadJsonContent('./abbreviations.json')
@description('The log analytics workspace name. If ommited will be generated')
param logAnalyticsWorkspaceName string = ''
param useApplicationInsights bool = true
param useContainerRegistry bool = true
var aiConfig = loadYamlContent('./ai.yaml')
@description('The name of the machine learning online endpoint. If ommited will be generated')
param resourceGroupName string = ''

@description('The API version of the OpenAI resource')
param openAiApiVersion string = '2023-07-01-preview'

@description('The name of the embedding model deployment')
param embeddingDeploymentName string = 'text-embedding-ada-002'

@description('The name of the teacher model deployment')
param teacherDeploymentName string = 'raft-teacher-llama-3-1-405B-chat'

@description('The name of the baseline model deployment')
param baselineDeploymentName string = 'raft-baseline-llama-2-7b-chat'

@description('Id of the user or app to assign application roles')
param principalId string = ''

@description('Whether the deployment is running on GitHub Actions')
param runningOnGh string = ''

@description('Whether the deployment is running on Azure DevOps Pipeline')
param runningOnAdo string = ''

var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))
var tags = { 'azd-env-name': environmentName }

resource resourceGroup 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: !empty(resourceGroupName) ? resourceGroupName : '${abbrs.resourcesResourceGroups}${environmentName}'
  location: location
  tags: tags
}

// USER ROLES
var principalType = empty(runningOnGh) && empty(runningOnAdo) ? 'User' : 'ServicePrincipal'
module managedIdentity 'core/security/managed-identity.bicep' = {
  name: 'managed-identity'
  scope: resourceGroup
  params: {
    name: 'id-${resourceToken}'
    location: location
    tags: tags
  }
}

module ai 'core/host/ai-environment.bicep' = {
  name: 'ai'
  scope: resourceGroup
  params: {
    location: location
    tags: tags
    hubName: !empty(aiHubName) ? aiHubName : 'ai-hub-${resourceToken}'
    projectName: !empty(aiProjectName) ? aiProjectName : 'ai-project-${resourceToken}'
    keyVaultName: !empty(keyVaultName) ? keyVaultName : '${abbrs.keyVaultVaults}${resourceToken}'
    storageAccountName: !empty(storageAccountName)
      ? storageAccountName
      : '${abbrs.storageStorageAccounts}${resourceToken}'
    openAiName: !empty(openAiName) ? openAiName : 'aoai-${resourceToken}'
    openAiConnectionName: !empty(openAiConnectionName) ? openAiConnectionName : 'aoai-connection'
    deployments: array(contains(aiConfig, 'deployments') ? aiConfig.deployments : [])
    logAnalyticsName: !useApplicationInsights
      ? ''
      : !empty(logAnalyticsWorkspaceName)
          ? logAnalyticsWorkspaceName
          : '${abbrs.operationalInsightsWorkspaces}${resourceToken}'
    applicationInsightsName: !useApplicationInsights
      ? ''
      : !empty(applicationInsightsName) ? applicationInsightsName : '${abbrs.insightsComponents}${resourceToken}'
    containerRegistryName: !useContainerRegistry
      ? ''
      : !empty(containerRegistryName) ? containerRegistryName : '${abbrs.containerRegistryRegistries}${resourceToken}'
  }
}

module appinsightsAccountRole 'core/security/role.bicep' = {
  scope: resourceGroup
  name: 'appinsights-account-role'
  params: {
    principalId: managedIdentity.outputs.managedIdentityPrincipalId
    roleDefinitionId: '3913510d-42f4-4e42-8a64-420c390055eb' // Monitoring Metrics Publisher
    principalType: 'ServicePrincipal'
  }
}

module openaiRoleUser 'core/security/role.bicep' = if (!empty(principalId)) {
  scope: resourceGroup
  name: 'user-openai-user'
  params: {
    principalId: principalId
    roleDefinitionId: '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd' //Cognitive Services OpenAI User
    principalType: principalType
  }
}

var teacherDeployment = length(ai.outputs.serverlessDeployments) == 1 
  ? ai.outputs.serverlessDeployments[0] 
  : first(filter(ai.outputs.serverlessDeployments, deployment => deployment.name == teacherDeploymentName))

var baselineDeployment = first(filter(ai.outputs.serverlessDeployments, deployment => deployment.name == baselineDeploymentName))

output AZURE_LOCATION string = location
output AZURE_RESOURCE_GROUP string = resourceGroup.name

output AZURE_WORKSPACE_NAME string = ai.outputs.projectName

output APPINSIGHTS_CONNECTIONSTRING string = ai.outputs.applicationInsightsConnectionString

output OPENAI_TYPE string = 'azure'

// Azure OpenAI environment variables
output EMBEDDING_AZURE_OPENAI_ENDPOINT string = ai.outputs.openAiEndpoint
output EMBEDDING_AZURE_OPENAI_DEPLOYMENT string = embeddingDeploymentName
output EMBEDDING_OPENAI_API_VERSION string = openAiApiVersion

// OpenAI environment variables
output COMPLETION_OPENAI_BASE_URL string = teacherDeployment.endpointUri
output COMPLETION_OPENAI_DEPLOYMENT string = teacherDeployment.name
output COMPLETION_OPENAI_API_KEY string = teacherDeployment.primaryKey

// OpenAI environment variables
output BASELINE_OPENAI_BASE_URL string = baselineDeployment.endpointUri
output BASELINE_OPENAI_DEPLOYMENT string = baselineDeployment.name
output BASELINE_OPENAI_API_KEY string = baselineDeployment.primaryKey
