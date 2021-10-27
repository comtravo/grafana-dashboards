package test

import (
	"fmt"
	"testing"

	"github.com/gruntwork-io/terratest/modules/random"
	"github.com/gruntwork-io/terratest/modules/terraform"
	"github.com/stretchr/testify/require"
)

func TestFirehose_noDashboard(t *testing.T) {

	dashboardName := fmt.Sprintf("firehose-%s", random.UniqueId())
	exampleDir := "../../examples/firehose_dashboards/no_dashboard/"

	terraformOptions := SetupExample(t, dashboardName, exampleDir)
	t.Logf("Terraform module inputs: %+v", *terraformOptions)
	defer terraform.Destroy(t, terraformOptions)

	terraformApplyOutput := terraform.InitAndApply(t, terraformOptions)
	resourceCount := terraform.GetResourceCount(t, terraformApplyOutput)

	require.Equal(t, resourceCount.Add, 0)
	require.Equal(t, resourceCount.Change, 0)
	require.Equal(t, resourceCount.Destroy, 0)

	output := terraform.OutputMap(t, terraformOptions, "op")

	expectedLen := 4
	expectedMap := map[string]string{
		"dashboard_id": "",
		"slug":         "",
		"uid":          "",
		"version":      "",
	}

	require.Len(t, output, expectedLen, "Output should contain %d items", expectedLen)
	require.Equal(t, expectedMap, output, "Map %q should match %q", expectedMap, output)
}

func TestFirehose_dashboard(t *testing.T) {
	t.Skip()
	dashboardName := fmt.Sprintf("firehose-%s", random.UniqueId())
	exampleDir := "../../examples/firehose_dashboards/dashboard/"

	terraformOptions := SetupExample(t, dashboardName, exampleDir)
	t.Logf("Terraform module inputs: %+v", *terraformOptions)
	defer terraform.Destroy(t, terraformOptions)

	TerraformApplyAndValidateOutputs(t, terraformOptions)
}

func TestFirehose_folder(t *testing.T) {

	t.Skip()

	dashboardName := fmt.Sprintf("firehose-%s", random.UniqueId())
	exampleDir := "../../examples/firehose_dashboards/dashboard_with_folder/"

	terraformOptions := SetupExample(t, dashboardName, exampleDir)
	t.Logf("Terraform module inputs: %+v", *terraformOptions)
	defer terraform.Destroy(t, terraformOptions)

	TerraformApplyAndValidateOutputs(t, terraformOptions)
}
