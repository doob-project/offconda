pipeline {
  agent any
  environment {
    CONDAENV = calc_conda_env()
    SOURCELABEL = 'pytho'
    TARGET = 'C:\\CONDAOFFLINE'
  }
  parameters {
    string(name: 'COLOR', defaultValue: 'PYTHO_0402', description: 'Version name of the whole solution')
    string(name: 'COMPONENTS', defaultValue: 'pytho==4.2 gsf_datamanagement==4.1.2 gsf==4.1.2', description: 'Final packages and their version')
  }
  stages {
    stage('SetUp') {
      steps {
        stash(name: "source", useDefaultExcludes: true)
      }
    }
    stage("Generating packages list") {
      steps {
        parallel(
          "Build on Windows": {
            builder("windows")
          },
          "Build on Linux": {
            builder("linux")
          }
        )
      }
    }
    stage('Downloading and indexing packages') {
      steps {
        unarchive(mapping: ["elencone-linux.txt": "elencone-linux.txt", "elencone-windows.txt": "elencone-windows.txt"])
        bat(script: "python download.py ${params.COLOR}")
        bat(script: "for /D %%d IN (${params.COLOR}\\*) DO call conda index %%d")
        // Solo indici, please!
        // archiveArtifacts artifacts: "${params.COLOR}/*/*.tag.bz2"
      }
    }
    stage('Copying packages') {
      steps {
        bat(script: "(robocopy /MIR ${params.COLOR} ${TARGET}\\${params.COLOR}) ^& IF %ERRORLEVEL% LEQ 1 exit 0")
      }
    }
  }
}


def calc_conda_env() {
    return "${env.JOB_NAME}_${env.BUILD_NUMBER}".replace('%2F','_').replace('/', '_')
}


def builder(envlabel, condaenvb="base") {
  node(envlabel) {
    pipeline {
      stage('Unstash') {
        unstash "source"
      }
      stage('Generating packages list') {
        condashellcmd("conda create -y -n ${CONDAENV} python=2.7", condaenvb)
        condashellcmd("conda install -c t/${env.ANACONDA_API_TOKEN}/prometeia/channel/${SOURCELABEL} -c t/${env.ANACONDA_API_TOKEN}/prometeia -c defaults --override-channels --channel-priority -y ${params.COMPONENTS}", "${CONDAENV}")
        script {
          writeFile file: "elencone-${envlabel}.txt", text: condashellcmd("conda list --explicit", "${CONDAENV}", true).trim()
        }
        archiveArtifacts artifacts: "elencone-${envlabel}.txt"
        condashellcmd("conda env remove -y -n ${CONDAENV}", condaenvb)
      }
      /*
      stage('TearDown') {
        deleteDir()
      } 
      */
    }
  }
}


void shellcmd(command, returnStdout=false, inPlace=False) {
  if (isUnix() && inPlace) {
    return sh(script: "source ${command}", returnStdout: returnStdout)
  } else if (isUnix()) {
    return sh(script: command, returnStdout: returnStdout)
  } else {
    return bat(script:command, returnStdout: returnStdout)
  }
}


void condashellcmd(command, condaenv, returnStdout=false) {
  if (isUnix()) {
    return sh(script: "source /home/jenkins/miniconda2/bin/activate ${condaenv}; ${command}", returnStdout: returnStdout)
  } else {
    return bat(script: "activate ${condaenv} && ${command} && deactivate", returnStdout: returnStdout)
  }
}
