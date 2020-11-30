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
        sh(label: 'Testing docker image', script: "make test-docker")
      }
    }
  }
}
