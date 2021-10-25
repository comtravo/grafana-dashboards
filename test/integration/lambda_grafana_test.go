package test

import (
	"fmt"
	"testing"

	"github.com/gruntwork-io/terratest/modules/random"
	"github.com/gruntwork-io/terratest/modules/terraform"
	"github.com/stretchr/testify/require"
)

func TestLambda_noDashboard(t *testing.T) {

	// t.Parallel()
	dashboardName := fmt.Sprintf("lambda-%s", random.UniqueId())
	exampleDir := "../../examples/lambda_dashboards/no_dashboard/"

	terraformOptions := SetupExample(t, dashboardName, exampleDir)
	t.Logf("Terraform module inputs: %+v", *terraformOptions)
	defer terraform.Destroy(t, terraformOptions)

	terraformApplyOutput := terraform.InitAndApply(t, terraformOptions)
	resourceCount := terraform.GetResourceCount(t, terraformApplyOutput)

	require.Equal(t, resourceCount.Add, 0)
	require.Equal(t, resourceCount.Change, 0)
	require.Equal(t, resourceCount.Destroy, 0)

	output := terraform.OutputMap(t, terraformOptions, "op")

	expectedLen := 2
	expectedMap := map[string]string{
		"dashboard_id": "",
		"slug":         "",
	}

	require.Len(t, output, expectedLen, "Output should contain %d items", expectedLen)
	require.Equal(t, expectedMap, output, "Map %q should match %q", expectedMap, output)
}

func TestLambda_lambda(t *testing.T) {

	// t.Parallel()
	dashboardName := fmt.Sprintf("lambda-%s", random.UniqueId())
	exampleDir := "../../examples/lambda_dashboards/lambda/"

	terraformOptions := SetupExample(t, dashboardName, exampleDir)
	t.Logf("Terraform module inputs: %+v", *terraformOptions)
	defer terraform.Destroy(t, terraformOptions)

	TerraformApplyAndValidateOutputs(t, terraformOptions)
}

func TestLambda_lambdaFolder(t *testing.T) {

	// t.Parallel()
	dashboardName := fmt.Sprintf("lambda-%s", random.UniqueId())
	exampleDir := "../../examples/lambda_dashboards/lambda_folder/"

	terraformOptions := SetupExample(t, dashboardName, exampleDir)
	t.Logf("Terraform module inputs: %+v", *terraformOptions)
	defer terraform.Destroy(t, terraformOptions)

	TerraformApplyAndValidateOutputs(t, terraformOptions)
}

func TestLambda_lambdaAlert(t *testing.T) {

	// t.Parallel()
	dashboardName := fmt.Sprintf("lambda-%s", random.UniqueId())
	exampleDir := "../../examples/lambda_dashboards/lambda_alert/"

	terraformOptions := SetupExample(t, dashboardName, exampleDir)
	t.Logf("Terraform module inputs: %+v", *terraformOptions)
	defer terraform.Destroy(t, terraformOptions)

	TerraformApplyAndValidateOutputs(t, terraformOptions)
}

func TestLambda_lambdaSnsSqsTrigger(t *testing.T) {

	// t.Parallel()
	dashboardName := fmt.Sprintf("lambda-%s", random.UniqueId())
	exampleDir := "../../examples/lambda_dashboards/lambda_sns_sqs_trigger/"

	terraformOptions := SetupExample(t, dashboardName, exampleDir)
	t.Logf("Terraform module inputs: %+v", *terraformOptions)
	defer terraform.Destroy(t, terraformOptions)

	TerraformApplyAndValidateOutputs(t, terraformOptions)
}

func SetupExample(t *testing.T, dashboardName string, exampleDir string) *terraform.Options {

	terraformOptions := &terraform.Options{
		TerraformDir: exampleDir,
		Vars: map[string]interface{}{
			"name": dashboardName,
		},
	}
	return terraformOptions
}

func TestLambda_lambdaSqsFifoTrigger(t *testing.T) {

	// t.Parallel()
	dashboardName := fmt.Sprintf("lambda-%s", random.UniqueId())
	exampleDir := "../../examples/lambda_dashboards/lambda_sqs_fifo_trigger/"

	terraformOptions := SetupExample(t, dashboardName, exampleDir)
	t.Logf("Terraform module inputs: %+v", *terraformOptions)
	defer terraform.Destroy(t, terraformOptions)

	TerraformApplyAndValidateOutputs(t, terraformOptions)
}

func SetupExample(t *testing.T, dashboardName string, exampleDir string) *terraform.Options {

	terraformOptions := &terraform.Options{
		TerraformDir: exampleDir,
		Vars: map[string]interface{}{
			"name": dashboardName,
		},
	}
	return terraformOptions
}

func TerraformApplyAndValidateOutputs(t *testing.T, terraformOptions *terraform.Options) {
	terraformApplyOutput := terraform.InitAndApply(t, terraformOptions)
	resourceCount := terraform.GetResourceCount(t, terraformApplyOutput)

	require.Greater(t, resourceCount.Add, 0)
	require.Equal(t, resourceCount.Change, 0)
	require.Equal(t, resourceCount.Destroy, 0)

	output := terraform.OutputMap(t, terraformOptions, "op")

	expectedLen := 2
	notExpectedMap := map[string]string{
		"dashboard_id": "",
		"slug":         "",
	}

	require.Len(t, output, expectedLen, "Output should contain %d items", expectedLen)
	require.NotEqual(t, output, notExpectedMap)
}
