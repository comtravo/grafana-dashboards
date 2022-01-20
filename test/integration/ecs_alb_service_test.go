package test

import (
	"fmt"
	"testing"

	"github.com/gruntwork-io/terratest/modules/random"
	"github.com/gruntwork-io/terratest/modules/terraform"
	"github.com/stretchr/testify/require"
)

func TestECSALBService_noDashboard(t *testing.T) {

	t.Parallel()
	dashboardName := fmt.Sprintf("ecs-%s", random.UniqueId())
	exampleDir := "../../examples/ecs_alb_service_dashboards/no_dashboard/"

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

func TestECSALBService_alert(t *testing.T) {

	t.Parallel()
	dashboardName := fmt.Sprintf("apig-%s", random.UniqueId())
	exampleDir := "../../examples/ecs_alb_service_dashboards/ecs_alb_service_alert/"

	terraformOptions := SetupExample(t, dashboardName, exampleDir)
	t.Logf("Terraform module inputs: %+v", *terraformOptions)
	defer terraform.Destroy(t, terraformOptions)

	TerraformApplyAndValidateOutputs(t, terraformOptions)
}

func TestECSALBService_noESDataSource(t *testing.T) {

	t.Parallel()
	dashboardName := fmt.Sprintf("apig-%s", random.UniqueId())
	exampleDir := "../../examples/ecs_alb_service_dashboards/ecs_alb_service_no_es_datasource/"

	terraformOptions := SetupExample(t, dashboardName, exampleDir)
	t.Logf("Terraform module inputs: %+v", *terraformOptions)
	defer terraform.Destroy(t, terraformOptions)

	TerraformApplyAndValidateOutputs(t, terraformOptions)
}

func TestECSALBService_folder(t *testing.T) {

	t.Parallel()
	dashboardName := fmt.Sprintf("apig-%s", random.UniqueId())
	exampleDir := "../../examples/ecs_alb_service_dashboards/ecs_alb_service_folder/"

	terraformOptions := SetupExample(t, dashboardName, exampleDir)
	t.Logf("Terraform module inputs: %+v", *terraformOptions)
	defer terraform.Destroy(t, terraformOptions)

	TerraformApplyAndValidateOutputs(t, terraformOptions)
}
