PROJECT = webhook
FUNCTION_NAME = kite-webhook
FUNCTION_HANDLER = kite_webhook_handler
FUNCTION_DESCRIPTION = "Dealing with github app webhook check_run POST event"

# run python linting test
flake8:
	flake8 **/*.py

# zip function file
zip:
	cd webhook && zip ../$(PROJECT).zip webhook.py

lambda_delete:
	aws lambda delete-function \
		--function-name $(FUNCTION_NAME)

lambda_create:
	aws lambda create-function \
		--region $(AWS_REGION) \
		--function-name $(FUNCTION_NAME) \
		--description $(FUNCTION_DESCRIPTION) \
		--zip-file fileb://./$(PROJECT).zip \
		--role $(SERVICE_ROLE) \
		--handler $(PROJECT).$(FUNCTION_HANDLER) \
		--runtime python3.8 \
		--timeout 15 \
		--memory-size 128 \
		--environment "Variables={GITHUB_ACCESS_TOKEN=AQICAHj7RSzG4JqNNnM3dbZox06sEvand3JdQiiNJGYlB80iiwGeA0+E/4Y5gvbpSek4WSw2AAAAhzCBhAYJKoZIhvcNAQcGoHcwdQIBADBwBgkqhkiG9w0BBwEwHgYJYIZIAWUDBAEuMBEEDDm4YNDaQCBgNMTpmQIBEIBDUYkHB86UaXLD+G/C2kfPlThw6m5vXwVLdKPGw7Ubgxz0PiIvWiq6RlmxPcVmVmaO0q6+D9MuRjWSqsAuRYdbRAewHg==, GITHUB_APP_WEBHOOK_SECRET=AQICAHj7RSzG4JqNNnM3dbZox06sEvand3JdQiiNJGYlB80iiwEbTQ5FKyvyVk/CdfIi5V44AAAAhzCBhAYJKoZIhvcNAQcGoHcwdQIBADBwBgkqhkiG9w0BBwEwHgYJYIZIAWUDBAEuMBEEDHCU546tiN7NWoCVoAIBEIBDlblVRV1Xq4hhmk0s3nMmmMBkmjMo7gJIXMOrPR3mHUlDo3+lYNiorphnBfiBQZkjSTVU7N2Fh7hRsh1BbkZlOD1Y0Q==, SQS_REGION=$(AWS_REGION), SQS_QUEUE=$(SQS_QUEUE)}" \
		--kms-key-arn $(KMS_KEY_ARN) \
		--tags name=kite-webhook

.PHONY: flake8 lambda_delete lambda_delete
