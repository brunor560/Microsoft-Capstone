# Azure OpenAI provisioning (azure-dev profile)

Reproducible setup for the cheap verification deployment. Run once per
subscription.

> **Region warning.** The USF tenant enforces an Azure Policy assignment
> limiting deployment regions to `mexicocentral`, `westus`, `canadacentral`,
> `denmarkeast`, `belgiumcentral`. Of those only **westus** and
> **canadacentral** support Azure OpenAI; `mexicocentral` is not a valid
> Cognitive Services location at all. **`eastus2` — used by nearly every
> Azure OpenAI tutorial — is blocked** and will fail with a policy error.
>
> Verify your own allowed regions before deploying:
> ```bash
> az policy assignment list \
>   --query "[].{name:displayName, params:parameters}" -o json
> ```

## 1. Register the resource provider

A fresh subscription has `Microsoft.CognitiveServices` unregistered, which
also makes quota queries return empty. Registration takes a few minutes.

```bash
az provider register --namespace Microsoft.CognitiveServices
az provider show --namespace Microsoft.CognitiveServices \
  --query registrationState -o tsv   # wait for "Registered"
```

## 2. Create the resource group and account

```bash
az group create -n rg-agentic-eval -l westus

az cognitiveservices account create \
  -n autogen-dev -g rg-agentic-eval \
  -l westus --kind OpenAI --sku S0
```

Azure appends a random suffix to the endpoint hostname, so **do not assume**
it matches the account name. Read it back:

```bash
az cognitiveservices account show -n autogen-dev -g rg-agentic-eval \
  --query properties.endpoint -o tsv
# e.g. https://autogen-dev-8cb0e.openai.azure.com/
```

## 3. Deploy the model

```bash
az cognitiveservices account deployment create \
  -g rg-agentic-eval -n autogen-dev \
  --deployment-name gpt-4.1-mini \
  --model-name gpt-4.1-mini --model-version 2025-04-14 \
  --model-format OpenAI \
  --sku-name GlobalStandard --sku-capacity 10
```

Capacity 10 ≈ 10K TPM, granted automatically on Azure for Students without a
quota-increase request. At the 15,000-token ceiling one run may span 1–2
minutes of rate-limited throughput.

List available models in an allowed region with:

```bash
az cognitiveservices model list --location westus -o json
```

## 4. Populate `.env`

```bash
cd pipeline/autogen

az cognitiveservices account keys list \
  -n autogen-dev -g rg-agentic-eval --query key1 -o tsv
```

Set in `.env` (gitignored — never commit):

```
AZURE_DEV_API_KEY=<key1>
AZURE_DEV_ENDPOINT=https://autogen-dev-8cb0e.openai.azure.com/
AZURE_DEV_DEPLOYMENT=gpt-4.1-mini
AZURE_DEV_API_VERSION=2024-10-21
```

## 5. Verify

```bash
./.venv/bin/python -m harness.smoke_test --model-profile azure-dev
```

Expected: `PHASE 0.5 GATE: PASSED` with non-zero token counts. Cost is ~14
tokens, a fraction of a cent.

## Future: RBAC instead of API keys

`AzureOpenAIChatCompletionClient` natively accepts `azure_ad_token_provider`,
and `azure-identity` is already installed as a transitive dependency of
`autogen-ext[azure]`. Switching to short-lived tokens requires:

1. `az login` (already done on this host),
2. assigning the `Cognitive Services OpenAI User` role on the account,
3. adding an `auth: azure_identity` branch in `harness/model_profiles.py`.

The subscription owner has **Owner**, so step 2 is available. Deferred for
now to keep one variable changing at a time; the only blast radius is
`build_client()`.
