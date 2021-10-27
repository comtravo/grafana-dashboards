package test

import (
	"fmt"
	"testing"

	"github.com/gruntwork-io/terratest/modules/random"
	"github.com/gruntwork-io/terratest/modules/terraform"
	"github.com/stretchr/testify/require"
)

func TestRDS_noDashboard(t *testing.T) {
	t.Parallel()
	dashboardName := fmt.Sprintf("rds-%s", random.UniqueId())
	exampleDir := "../../examples/rds_dashboards/no_dashboard/"

	terraformOptions := SetupExample(t, dashboardName, exampleDir)
	t.Logf("Terraform module inputs: %+v", *terraformOptions)
	defer terraform.Destroy(t, terraformOptions)

	terraformApplyOutput := terraform.InitAndApply(t, terraformOptions)
	resourceCount := terraform.GetResourceCount(t, terraformApplyOutput)

	require.Equal(t, resourceCount.Add, 0)
	require.Equal(t, resourceCount.Change, 0)
	require.Equal(t, resourceCount.Destroy, 0)
}

func TestRDS_dashboard(t *testing.T) {
	t.Parallel()
	dashboardName := fmt.Sprintf("rds-%s", random.UniqueId())
	exampleDir := "../../examples/rds_dashboards/dashboard/"

	terraformOptions := SetupExample(t, dashboardName, exampleDir)
	t.Logf("Terraform module inputs: %+v", *terraformOptions)
	defer terraform.Destroy(t, terraformOptions)

	TerraformApplyAndValidateOutputs(t, terraformOptions)
}

func TestRDS_folder(t *testing.T) {
	t.Parallel()
	dashboardName := fmt.Sprintf("rds-%s", random.UniqueId())
	exampleDir := "../../examples/rds_dashboards/dashboard_with_folder/"

	terraformOptions := SetupExample(t, dashboardName, exampleDir)
	t.Logf("Terraform module inputs: %+v", *terraformOptions)
	defer terraform.Destroy(t, terraformOptions)

	TerraformApplyAndValidateOutputs(t, terraformOptions)
}
