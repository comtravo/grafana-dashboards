package test

import (
	"fmt"
	"testing"

	"github.com/gruntwork-io/terratest/modules/random"
	"github.com/gruntwork-io/terratest/modules/terraform"
	"github.com/stretchr/testify/require"
)

func TestStepFunction_noDashboard(t *testing.T) {

	dashboardName := fmt.Sprintf("sfn-%s", random.UniqueId())
	exampleDir := "../../examples/step_function_dashboards/no_dashboard/"

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

func TestStepFunction_alert(t *testing.T) {

	dashboardName := fmt.Sprintf("sfn-%s", random.UniqueId())
	exampleDir := "../../examples/step_function_dashboards/step_function_alert/"

	terraformOptions := SetupExample(t, dashboardName, exampleDir)
	t.Logf("Terraform module inputs: %+v", *terraformOptions)
	defer terraform.Destroy(t, terraformOptions)

	TerraformApplyAndValidateOutputs(t, terraformOptions)
}

func TestStepFunction_folder(t *testing.T) {

	dashboardName := fmt.Sprintf("sfn-%s", random.UniqueId())
	exampleDir := "../../examples/step_function_dashboards/step_function_folder/"

	terraformOptions := SetupExample(t, dashboardName, exampleDir)
	t.Logf("Terraform module inputs: %+v", *terraformOptions)
	defer terraform.Destroy(t, terraformOptions)

	TerraformApplyAndValidateOutputs(t, terraformOptions)
}

func TestStepFunction_withoutLambda(t *testing.T) {

	dashboardName := fmt.Sprintf("sfn-%s", random.UniqueId())
	exampleDir := "../../examples/step_function_dashboards/step_function_without_lambda/"

	terraformOptions := SetupExample(t, dashboardName, exampleDir)
	t.Logf("Terraform module inputs: %+v", *terraformOptions)
	defer terraform.Destroy(t, terraformOptions)

	TerraformApplyAndValidateOutputs(t, terraformOptions)
}
