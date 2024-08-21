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

@description('The name of the 35 turbo OpenAI deployment')
param openAi_35_turbo_DeploymentName string = 'gpt-35-turbo'


@description('The name of the 4 OpenAI deployment')
param openAi_4_DeploymentName string = 'gpt-4'


@description('The name of the 4 eval OpenAI deployment')
param openAi_4_eval_DeploymentName string = 'gpt-4-evals'

@description('The name of the OpenAI embedding deployment')
param openAiEmbeddingDeploymentName string = 'text-embedding-ada-002'

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

output AZURE_LOCATION string = location
output AZURE_RESOURCE_GROUP string = resourceGroup.name

output AZURE_OPENAI_35_TURBO_DEPLOYMENT_NAME string = openAi_35_turbo_DeploymentName
output AZURE_OPENAI_DEPLOYMENT_NAME string = openAi_4_DeploymentName
output AZURE_OPENAI_4_EVAL_DEPLOYMENT_NAME string = openAi_4_eval_DeploymentName
output AZURE_OPENAI_API_VERSION string = openAiApiVersion
output AZURE_OPENAI_ENDPOINT string = ai.outputs.openAiEndpoint
output AZURE_OPENAI_NAME string = ai.outputs.openAiName
output AZURE_OPENAI_RESOURCE_GROUP string = resourceGroup.name
output AZURE_OPENAI_RESOURCE_GROUP_LOCATION string = resourceGroup.location

output APPINSIGHTS_CONNECTIONSTRING string = ai.outputs.applicationInsightsConnectionString

output OPENAI_TYPE string = 'azure'
output AZURE_EMBEDDING_NAME string = openAiEmbeddingDeploymentName
