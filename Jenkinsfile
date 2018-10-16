@Library(['promebuilder', 'offconda'])_


pipeline {
  agent any
  parameters {
    string(
        name: 'QUARTERLY',
        description: 'Version name of the whole solution (e.g. "PYTHO_0402")',
        defaultValue: env.BRANCH_NAME
    )
    string(
        name: 'COMPONENTS',
        description: 'Final packages and their version (e.g. "pytho==4.3.* gsf==4.3.* ratingpro==3.4.0 serversoa==1.0.* pytho_docs==4.3.* conda python==2.7.*")',
        defaultValue: 'pytho gsf ratingpro serversoa pytho_docs python==2.7.* conda==4.5.*'
    )
    string(
        name: 'LABEL',
        defaultValue: 'develop',
        description: 'Source channel'
    )
    string(
        name: 'TARGET',
        defaultValue: 'C:\\CONDAOFFLINE',
        description: 'Target offline repository'
    )
  }
  environment {
    CONDAENV = "${env.JOB_NAME}_${env.BUILD_NUMBER}".replace('%2F','_').replace('/', '_')
  }
  stages {
    stage('Bootstrap') {
      steps {
        echo "NB: The packages should be PRIVATE o PUBLIC, it doesn't work with 'authentication required'."
        stash(name: "source", useDefaultExcludes: true)
      }
    }
    stage("PackageList") {
      parallel {
        stage("Build on Linux") {
          steps {
            doublePackager('linux', params.LABEL, params.COMPONENTS)
          }
        }
        stage("Build on Windows") {
          steps {
            doublePackager('windows', params.LABEL, params.COMPONENTS)
          }
        }
      }
    }
    stage('Downloading and indexing packages') {
      steps {
        unarchive(mapping: ["elencone-linux.txt": "elencone-linux.txt", "elencone-windows.txt": "elencone-windows.txt"])
        bat(script: "python download.py ${params.QUARTERLY}")
        bat(script: "for /D %%d IN (${params.QUARTERLY}\\*) DO call conda index %%d")
        // Solo indici, please!
        // archiveArtifacts artifacts: "${params.QUARTERLY}/*/*.tag.bz2"
      }
    }
    stage('Copying packages') {
      steps {
        bat(script: "(robocopy /MIR ${params.QUARTERLY} ${TARGET}\\${params.QUARTERLY}) ^& IF %ERRORLEVEL% LEQ 1 exit 0")
      }
    }
  }
  post {
    success {
      slackSend color: "good", message: "Successed ${env.JOB_NAME} (<${env.BUILD_URL}|Open>)"
      deleteDir()
    }
    failure {
      slackSend color: "warning", message: "Failed ${env.JOB_NAME} (<${env.BUILD_URL}|Open>)"
    }
  }
}
