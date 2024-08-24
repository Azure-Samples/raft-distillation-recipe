#!/bin/bash
set -e

DIR="$( cd "$( dirname "$0" )" && pwd )"

# That script requires bash and azd only supports sh
bash ${DIR}/export_env.sh

echo "Exporting config.json"
cat > config.json <<EOF
{
    "subscription_id": "${AZURE_SUBSCRIPTION_ID}",
    "resource_group": "${AZURE_RESOURCE_GROUP}",
    "workspace_name": "${AZURE_WORKSPACE_NAME}"
}
EOF

bash ${DIR}/tests.sh
