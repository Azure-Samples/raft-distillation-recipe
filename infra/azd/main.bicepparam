using './main.bicep'

param environmentName = readEnvironmentVariable('AZURE_ENV_NAME', 'MY_ENV')
param location = readEnvironmentVariable('AZURE_LOCATION', 'eastus2')
param principalId = readEnvironmentVariable('AZURE_PRINCIPAL_ID', '')
param resourceGroupName = readEnvironmentVariable('AZURE_RESOURCE_GROUP', '')

param aiHubName = readEnvironmentVariable('AZUREAI_HUB_NAME', '')
param aiProjectName = readEnvironmentVariable('AZUREAI_PROJECT_NAME', '')

param openAiName = readEnvironmentVariable('AZURE_OPENAI_NAME', '')

param applicationInsightsName = readEnvironmentVariable('AZURE_APPLICATION_INSIGHTS_NAME', '')
param keyVaultName = readEnvironmentVariable('AZURE_KEYVAULT_NAME', '')
param storageAccountName = readEnvironmentVariable('AZURE_STORAGE_ACCOUNT_NAME', '')
param logAnalyticsWorkspaceName = readEnvironmentVariable('AZURE_LOG_ANALYTICS_WORKSPACE_NAME', '')

param useContainerRegistry = bool(readEnvironmentVariable('USE_CONTAINER_REGISTRY', 'true'))
param useApplicationInsights = bool(readEnvironmentVariable('USE_APPLICATION_INSIGHTS', 'true'))