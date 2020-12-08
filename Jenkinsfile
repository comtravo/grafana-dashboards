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
            sh(label: 'lint', script: "make lint-docker")
            sh(label: 'test', script: "make test-docker")
          } finally {
            sh(label: 'tear down', script: "make down")
          }
        }
      }
    }
  }
}
