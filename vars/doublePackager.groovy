#!/usr/bin/env groovy

def call(envlabel, sourcelabel, components, condaenvb="base") {
  node(envlabel) {
    pipeline {
      stage('Unstash') {
        unstash "source"
      }
      stage('Generating packages list') {
        condaShellCmd("conda create -y -n ${CONDAENV} python=2.7", condaenvb)
        retry(3) {
            condaShellCmd("conda install -q -c t/${env.ANACONDA_API_TOKEN}/prometeia/channel/${sourcelabel} -c t/${env.ANACONDA_API_TOKEN}/prometeia -c defaults --override-channels --no-channel-priority -y ${components}", "${CONDAENV}")
        }
        script {
          writeFile file: "elencone-${envlabel}.txt", text: condaShellCmd("conda list --explicit", "${CONDAENV}", true).trim()
        }
      }
      stage('ArtifactTearDown') {
        archiveArtifacts artifacts: "elencone-${envlabel}.txt"
        condaShellCmd("conda env remove -y -n ${CONDAENV}", condaenvb)
        deleteDir()
      }
    }
  }
}
