pipeline {

  agent { label 'worker' }

  options {
    ansiColor('gnome-terminal')
    buildDiscarder(logRotator(numToKeepStr: '30'))
    skipDefaultCheckout()
    timestamps()
  }

  stages {
    stage("Checkout SCM") {
      steps {
        script {
          ctCheckout(revision: getMultiBranchName(), wipeWorkspace: true, noTags: true, url: 'git@github.com:comtravo/grafana-dashboards.git')
        }
      }
    }

    stage("Build and Test") {
      steps {
        sh(label: 'Building docker image', script: "make build")

        script {
          try {
            sh(label: 'Lint docker image', script: "make lint-docker")
            sh(label: 'Tests', script: "make test-docker")
          } finally {
            sh(label: 'Teardown', script: "make test-docker")
          }
        }
      }
    }
  }
}
