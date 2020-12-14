package test

import (
	"fmt"
	"testing"

	"github.com/gruntwork-io/terratest/modules/random"
	"github.com/gruntwork-io/terratest/modules/terraform"
	"github.com/stretchr/testify/require"
)

func TestElasticsearch_noDashboard(t *testing.T) {

	dashboardName := fmt.Sprintf("es-%s", random.UniqueId())
	exampleDir := "../../examples/elasticsearch_dashboards/no_dashboard/"

	terraformOptions := SetupExample(t, dashboardName, exampleDir)
	t.Logf("Terraform module inputs: %+v", *terraformOptions)
	defer terraform.Destroy(t, terraformOptions)

	terraformApplyOutput := terraform.InitAndApply(t, terraformOptions)
	resourceCount := terraform.GetResourceCount(t, terraformApplyOutput)

	require.Equal(t, resourceCount.Add, 0)
	require.Equal(t, resourceCount.Change, 0)
	require.Equal(t, resourceCount.Destroy, 0)
}

func TestElasticsearch_dashboard(t *testing.T) {

	dashboardName := fmt.Sprintf("es-%s", random.UniqueId())
	exampleDir := "../../examples/elasticsearch_dashboards/dashboard/"

	terraformOptions := SetupExample(t, dashboardName, exampleDir)
	t.Logf("Terraform module inputs: %+v", *terraformOptions)
	defer terraform.Destroy(t, terraformOptions)

	TerraformApplyAndValidateElasticsearchOutputs(t, terraformOptions)
}

func TestElasticsearch_folder(t *testing.T) {

	dashboardName := fmt.Sprintf("es-%s", random.UniqueId())
	exampleDir := "../../examples/elasticsearch_dashboards/dashboard_with_folder/"

	terraformOptions := SetupExample(t, dashboardName, exampleDir)
	t.Logf("Terraform module inputs: %+v", *terraformOptions)
	defer terraform.Destroy(t, terraformOptions)

	TerraformApplyAndValidateElasticsearchOutputs(t, terraformOptions)
}

func TerraformApplyAndValidateElasticsearchOutputs(t *testing.T, terraformOptions *terraform.Options) {
	terraformApplyOutput := terraform.InitAndApply(t, terraformOptions)
	resourceCount := terraform.GetResourceCount(t, terraformApplyOutput)

	require.Greater(t, resourceCount.Add, 0)
	require.Equal(t, resourceCount.Change, 0)
	require.Equal(t, resourceCount.Destroy, 0)
}
