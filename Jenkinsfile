pipeline {
  agent any
  stages {
    stage('Install') {
      steps {
        sh '''#!/bin/bash -xe
/usr/local/anaconda3/condabin/conda activate jupyterhub
python setup.py install'''
      }
    }
  }
}
