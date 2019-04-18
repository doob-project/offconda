@Library(['promebuilder', 'offconda'])_


pipeline {
  agent any
  parameters {
    string(
        name: 'COMPONENTS',
        description: 'Forced Final packages and version',
        defaultValue: ''
    )
    string(
        name: 'LABEL',
        defaultValue: env.TAG_NAME ? (env.TAG_NAME.contains('rc') ? 'release' : 'main') : env.BRANCH_NAME.split('/')[0].replace('hotfix', 'release').replace('master', 'main'),
        description: 'Source label'
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
        writeFile file: 'components.txt', text: (params.COMPONENTS ? params.COMPONENTS : readFile('versions.txt'))
        archiveArtifacts artifacts: "components.txt"
        stash(name: "source", useDefaultExcludes: true)
      }
    }
    stage("Packages Discovery") {
      parallel {
        stage("Target Linux") {
          steps {
            doublePackager('linux', params.LABEL, readFile("components.txt") + " " + readFile("linux.txt"))
          }
        }
        stage("Target Linux Legacy") {
          steps {
             doublePackager('linux-legacy', params.LABEL, readFile("components.txt") + " " + readFile("linux-legacy.txt"))
          }
        }
        stage("Target Windows") {
          steps {
            doublePackager('windows', params.LABEL, readFile("components.txt") + " " + readFile("windows.txt"))
          }
        }
      }
    }

    stage('Packages Downloading and Indexing') {
      when {
        buildingTag()
      }
      steps {
        unarchive(mapping: ["elencone-linux.txt": "elencone-linux.txt", "elencone-windows.txt": "elencone-windows.txt"])
        bat(script: "python download.py ${env.TAG_NAME}")
        bat(script: "call conda index ${env.TAG_NAME}")
      }
    }
    stage('Checking Distribution') {
      when {
        buildingTag()
      }
      steps {
        bat(script: "python distrocheck.py ${env.TAG_NAME}")
      }
    }

    stage('Packages Downloading and Indexing - Legacy') {
      when {
        buildingTag()
      }
      steps {
        unarchive(mapping: ["elencone-linux-legacy.txt": "elencone-linux-legacy.txt"])
        bat(script: "python download.py ${env.TAG_NAME}-legacy elencone-linux-legacy.txt")
        bat(script: "call conda index ${env.TAG_NAME}-legacy")
      }
    }
    stage('Checking Distribution - Legacy') {
      when {
        buildingTag()
      }
      steps {
        bat(script: "python distrocheck.py ${env.TAG_NAME}-legacy")
      }
    }

    stage ('Distribution publish confirm') {
      steps {
        timeout(time: 1, unit: “HOURS”) {
          input(message: "Ready to publish the distributions?", ok: "OK, publish now!"
        }
      }
    }

    stage('Publishing Distribution') {
      when {
        buildingTag()
      }
      steps {
        bat(script: "(robocopy /MIR ${env.TAG_NAME} ${params.TARGET}\\${env.TAG_NAME} /XD ${env.TAG_NAME}\\win-64\\.cache ${env.TAG_NAME}\\linux-64\\.cache ${env.TAG_NAME}\\noarch\\.cache ) ^& IF %ERRORLEVEL% LEQ 1 exit 0")
      }
    }
    stage('Testing Distribution') {
      when {
        buildingTag()
      }
      steps {
        bat(script: "conda install pytho ratingpro serversoa -c http://daa-ws-01:9200/.condaoffline/${env.TAG_NAME} --override-channels --dry-run")
        node('linux') {
          sh(script: "conda install pytho ratingpro serversoa -c http://daa-ws-01:9200/.condaoffline/${env.TAG_NAME} --override-channels --dry-run")
        }
      }
    }
    stage('Publishing Distribution - Legacy') {
      when {
        buildingTag()
      }
      steps {
        bat(script: "(robocopy /MIR ${env.TAG_NAME}-legacy ${params.TARGET}\\${env.TAG_NAME}-legacy /XD ${env.TAG_NAME}-legacy\\linux-64\\.cache ${env.TAG_NAME}\\noarch\\.cache ) ^& IF %ERRORLEVEL% LEQ 1 exit 0")
      }
    }
    stage('Testing Distribution - Legacy') {
      when {
        buildingTag()
      }
      steps {
        node('linux') {
          sh(script: "conda install pytho ratingpro serversoa -c http://daa-ws-01:9200/.condaoffline/${env.TAG_NAME}-legacy --override-channels --dry-run")
        }
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
