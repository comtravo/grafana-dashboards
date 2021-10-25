package test

import (
	"fmt"
	"testing"

	"github.com/gruntwork-io/terratest/modules/random"
	"github.com/gruntwork-io/terratest/modules/terraform"
	"github.com/stretchr/testify/require"
)

func TestElasticacheRedis_noDashboard(t *testing.T) {

	dashboardName := fmt.Sprintf("elasticache-%s", random.UniqueId())
	exampleDir := "../../examples/elasticache_redis_dashboards/no_dashboard/"

	terraformOptions := SetupExample(t, dashboardName, exampleDir)
	t.Logf("Terraform module inputs: %+v", *terraformOptions)
	defer terraform.Destroy(t, terraformOptions)

	terraformApplyOutput := terraform.InitAndApply(t, terraformOptions)
	resourceCount := terraform.GetResourceCount(t, terraformApplyOutput)

	require.Equal(t, resourceCount.Add, 0)
	require.Equal(t, resourceCount.Change, 0)
	require.Equal(t, resourceCount.Destroy, 0)
}

func TestElasticacheRedis_dashboard(t *testing.T) {

	dashboardName := fmt.Sprintf("elasticache-%s", random.UniqueId())
	exampleDir := "../../examples/elasticache_redis_dashboards/dashboard/"

	terraformOptions := SetupExample(t, dashboardName, exampleDir)
	t.Logf("Terraform module inputs: %+v", *terraformOptions)
	defer terraform.Destroy(t, terraformOptions)

	TerraformApplyAndValidateElasticacheRedisOutputs(t, terraformOptions)
}

func TestElasticacheRedis_folder(t *testing.T) {

	dashboardName := fmt.Sprintf("elasticache-%s", random.UniqueId())
	exampleDir := "../../examples/elasticache_redis_dashboards/dashboard_with_folder/"

	terraformOptions := SetupExample(t, dashboardName, exampleDir)
	t.Logf("Terraform module inputs: %+v", *terraformOptions)
	defer terraform.Destroy(t, terraformOptions)

	TerraformApplyAndValidateElasticacheRedisOutputs(t, terraformOptions)
}

func TerraformApplyAndValidateElasticacheRedisOutputs(t *testing.T, terraformOptions *terraform.Options) {
	terraformApplyOutput := terraform.InitAndApply(t, terraformOptions)
	resourceCount := terraform.GetResourceCount(t, terraformApplyOutput)

	require.Greater(t, resourceCount.Add, 0)
	require.Equal(t, resourceCount.Change, 0)
	require.Equal(t, resourceCount.Destroy, 0)

	output := terraform.OutputMap(t, terraformOptions, "op")
	expectedLen := 4
	require.Len(t, output, expectedLen, "Output should contain %d items", expectedLen)
}
